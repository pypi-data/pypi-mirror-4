# -*- coding: utf-8 -*-
"""
Compiling extension classes works as follows:

    * Create an extension Numba/minivect type holding a symtab
    * Capture attribute types in the symtab ...

        * ... from the class attributes:

            @jit
            class Foo(object):
                attr = double

        * ... from __init__

            @jit
            class Foo(object):
                def __init__(self, attr):
                    self.attr = double(attr)

    * Type infer all methods
    * Compile all extension methods

        * Process signatures such as @void(double)
        * Infer native attributes through type inference on __init__
        * Path the extension type with a native attributes struct
        * Infer types for all other methods
        * Update the ext_type with a vtab type
        * Compile all methods

    * Create descriptors that wrap the native attributes
    * Create an extension type:

      {
        PyObject_HEAD
        ...
        virtual function table (func **)
        native attributes
      }

    The virtual function table (vtab) is a ctypes structure set as
    attribute of the extension types. Objects have a direct pointer
    for efficiency.

See also extension_types.pyx
"""
from __future__ import print_function, division, absolute_import


import types
import ctypes
import logging
import warnings
import inspect

import numba
from numba import pipeline, error, symtab
from numba import typesystem
from numba.minivect import minitypes
from . import extension_types

logger = logging.getLogger(__name__)

#------------------------------------------------------------------------
# Parse method signatures
#------------------------------------------------------------------------

def validate_method(py_func, sig, is_static):
    assert isinstance(py_func, types.FunctionType)
    nargs = py_func.__code__.co_argcount - 1 + is_static
    if len(sig.args) != nargs:
        raise error.NumbaError(
            "Expected %d argument types in function "
            "%s (don't include 'self')" % (nargs, py_func.__name__))

def get_signature(ext_type, is_class, is_static, sig):
    """
    Create a signature given the user-specified signature. E.g.

        class Foo(object):
            @void()                 # becomes: void(ext_type(Foo))
            def method(self): ...
    """
    if is_static:
        leading_arg_types = ()
    elif is_class:
        leading_arg_types = (numba.object_,)
    else:
        leading_arg_types = (ext_type,)

    argtypes = leading_arg_types + sig.args
    restype = sig.return_type
    return minitypes.FunctionType(return_type=restype, args=argtypes)

def get_classmethod_func(func):
    """
    Get the Python function the classmethod or staticmethod is wrapping.

    In Python2.6 classmethod and staticmethod don't have the '__func__'
    attribute.
    """
    if isinstance(func, classmethod):
        return func.__get__(object()).__func__
    else:
        assert isinstance(func, staticmethod)
        return func.__get__(object())

def _process_signature(ext_type, method, default_signature,
                       is_static=False, is_class=False):
    """
    Verify a method signature.

    Returns a Method object and the resolved signature.
    """
    if isinstance(method, types.FunctionType):
        # Process function
        if default_signature is None:
            # TODO: support deferred type inference and autojit methods
            raise error.NumbaError(
                "Method '%s' does not have signature" % (method.__name__,))
        validate_method(method, default_signature or numba.object_(),
                        is_static)
        if default_signature is None:
            default_signature = minitypes.FunctionType(return_type=None,
                                                       args=[])
        sig = get_signature(ext_type, is_class, is_static, default_signature)
        return Method(method, is_class, is_static), sig.return_type, sig.args
    elif isinstance(method, minitypes.Function):
        # @double(...)
        # def func(self, ...): ...
        return _process_signature(ext_type, method.py_func,
                                  method.signature, is_static, is_class)
    else:
        # Process staticmethod and classmethod
        if isinstance(method, staticmethod):
            is_static = True
        elif isinstance(method, classmethod):
            is_class = True
        else:
            return None, None, None

        return _process_signature(
                    ext_type, get_classmethod_func(method),
                    default_signature, is_static=is_static, is_class=is_class)

class Method(object):
    """
    py_func: the python 'def' function
    """

    def __init__(self, py_func, is_class, is_static):
        self.py_func = py_func
        py_func.live_objects = []
        self.is_class = is_class
        self.is_static = is_static
        self.name = py_func.__name__

    def result(self, py_func):
        if self.is_class:
            return classmethod(py_func)
        elif self.is_static:
            return staticmethod(py_func)
        else:
            return py_func

#------------------------------------------------------------------------
# Populate Extension Type with Methods
#------------------------------------------------------------------------

def _process_method_signatures(class_dict, ext_type):
    """
    Process all method signatures:

        * Verify signatures
        * Populate ext_type with method signatures (ExtMethodType)
    """
    for method_name, method in class_dict.iteritems():
        default_signature = None
        if (method_name == '__init__' and
                isinstance(method, types.FunctionType)):
            if inspect.getargspec(method).args:
                warnings.warn(
                    "Constructor for class '%s' has no signature, "
                    "assuming arguments have type 'object'" %
                                        ext_type.py_class.__name__)
            argtypes = [numba.object_] * (method.__code__.co_argcount - 1)
            default_signature = numba.void(*argtypes)

        method, restype, argtypes = _process_signature(ext_type, method,
                                                       default_signature)
        if method is None:
            continue

        signature = typesystem.ExtMethodType(
                    return_type=restype, args=argtypes, name=method.name,
                    is_class=method.is_class, is_static=method.is_static)
        ext_type.add_method(method_name, signature)
        class_dict[method_name] = method

def _type_infer_method(env, ext_type, method, method_name, class_dict, flags):
    if method_name not in ext_type.methoddict:
        return

    signature = ext_type.get_signature(method_name)
    restype, argtypes = signature.return_type, signature.args

    class_dict[method_name] = method
    func_signature, symtab, ast = pipeline.infer_types2(
                        env, method.py_func, restype, argtypes, **flags)
    ext_type.add_method(method_name, func_signature)

def _type_infer_init_method(env, class_dict, ext_type, flags):
    initfunc = class_dict.get('__init__', None)
    if initfunc is None:
        return

    _type_infer_method(env, ext_type, initfunc, '__init__', class_dict, flags)

def _type_infer_methods(env, class_dict, ext_type, flags):
    for method_name, method in class_dict.iteritems():
        if method_name in ('__new__', '__init__') or method is None:
            continue

        _type_infer_method(env, ext_type, method, method_name, class_dict, flags)

def _compile_methods(class_dict, env, ext_type, lmethods, method_pointers,
                     flags):
    parent_method_pointers = getattr(
                    ext_type.py_class, '__numba_method_pointers', None)
    for i, (method_name, func_signature) in enumerate(ext_type.methods):
        if method_name not in class_dict:
            # Inherited method
            assert parent_method_pointers is not None
            name, p = parent_method_pointers[i]
            assert name == method_name
            method_pointers.append((method_name, p))
            continue

        method = class_dict[method_name]
        # Don't use compile_after_type_inference, re-infer, since we may
        # have inferred some return types
        # TODO: delayed types and circular calls/variable assignments
        logger.debug(method.py_func)
        func_env = pipeline.compile2(
            env, method.py_func, func_signature.return_type,
            func_signature.args, name=method.py_func.__name__,
            **flags)
        lmethods.append(func_env.lfunc)
        method_pointers.append((method_name, func_env.translator.lfunc_pointer))
        class_dict[method_name] = method.result(func_env.numba_wrapper_func)

#------------------------------------------------------------------------
# Build Attributes Struct
#------------------------------------------------------------------------

def _construct_native_attribute_struct(ext_type):
    """
    Create attribute struct type from symbol table.
    """
    attrs = dict((name, var.type) for name, var in ext_type.symtab.iteritems())
    if ext_type.attribute_struct is None:
        # No fields to inherit
        ext_type.attribute_struct = numba.struct(**attrs)
    else:
        # Inherit fields from parent
        fields = []
        for name, variable in ext_type.symtab.iteritems():
            if name not in ext_type.attribute_struct.fielddict:
                fields.append((name, variable.type))
                ext_type.attribute_struct.fielddict[name] = variable.type

        # Sort fields by rank
        fields = numba.struct(fields).fields
        ext_type.attribute_struct.fields.extend(fields)

def _create_descr(attr_name):
    """
    Create a descriptor that accesses the attribute on the ctypes struct.
    """
    def _get(self):
        return getattr(self._numba_attrs, attr_name)
    def _set(self, value):
        return setattr(self._numba_attrs, attr_name, value)
    return property(_get, _set)

def inject_descriptors(env, py_class, ext_type, class_dict):
    "Cram descriptors into the class dict"
    for attr_name, attr_type in ext_type.symtab.iteritems():
        descriptor = _create_descr(attr_name)
        class_dict[attr_name] = descriptor

#------------------------------------------------------------------------
# Attribute Inheritance
#------------------------------------------------------------------------

def is_numba_class(cls):
    return hasattr(cls, '__numba_struct_type')

def verify_base_class_compatibility(cls, struct_type, vtab_type):
    "Verify that we can build a compatible class layout"
    bases = [cls]
    for base in cls.__bases__:
        if is_numba_class(base):
            attr_prefix = base.__numba_struct_type.is_prefix(struct_type)
            method_prefix = base.__numba_vtab_type.is_prefix(vtab_type)
            if not attr_prefix or not method_prefix:
                raise error.NumbaError(
                            "Multiple incompatible base classes found: "
                            "%s and %s" % (base, bases[-1]))

            bases.append(base)

def inherit_attributes(ext_type, class_dict):
    "Inherit attributes and methods from superclasses"
    cls = ext_type.py_class
    if not is_numba_class(cls):
        # superclass is not a numba class
        return

    struct_type = cls.__numba_struct_type
    vtab_type = cls.__numba_vtab_type
    verify_base_class_compatibility(cls, struct_type, vtab_type)

    # Inherit attributes
    ext_type.attribute_struct = numba.struct(struct_type.fields)
    for field_name, field_type in ext_type.attribute_struct.fields:
        ext_type.symtab[field_name] = symtab.Variable(field_type,
                                                      promotable_type=False)

    # Inherit methods
    for method_name, method_type in vtab_type.fields:
        func_signature = method_type.base_type
        args = list(func_signature.args)
        if not (func_signature.is_class or func_signature.is_static):
            args[0] = ext_type
        func_signature = func_signature.return_type(*args)
        ext_type.add_method(method_name, func_signature)

    ext_type.parent_attr_struct = struct_type
    ext_type.parent_vtab_type = vtab_type

def process_class_attribute_types(ext_type, class_dict):
    """
    Process class attribute types:

        @jit
        class Foo(object):

            attr = double
    """
    for name, value in class_dict.iteritems():
        if isinstance(value, minitypes.Type):
            ext_type.symtab[name] = symtab.Variable(value, promotable_type=False)

#------------------------------------------------------------------------
# Compile Methods and Build Attributes
#------------------------------------------------------------------------

def compile_extension_methods(env, py_class, ext_type, class_dict, flags):
    """
    Compile extension methods:

        1) Process signatures such as @void(double)
        2) Infer native attributes through type inference on __init__
        3) Path the extension type with a native attributes struct
        4) Infer types for all other methods
        5) Update the ext_type with a vtab type
        6) Compile all methods
    """
    method_pointers = []
    lmethods = []

    class_dict['__numba_py_class'] = py_class

    _process_method_signatures(class_dict, ext_type)
    _type_infer_init_method(env, class_dict, ext_type, flags)
    _construct_native_attribute_struct(ext_type)
    _type_infer_methods(env, class_dict, ext_type, flags)

    # TODO: patch method call types

    # Set vtab type before compiling
    ext_type.vtab_type = numba.struct(
        [(field_name, field_type.pointer())
         for field_name, field_type in ext_type.methods])
    _compile_methods(class_dict, env, ext_type, lmethods, method_pointers,
                     flags)
    return method_pointers, lmethods

#------------------------------------------------------------------------
# Virtual Methods
#------------------------------------------------------------------------

def vtab_name(field_name):
    "Mangle method names for the vtab (ctypes doesn't handle this)"
    if field_name.startswith("__") and field_name.endswith("__"):
        field_name = '__numba_' + field_name.strip("_")
    return field_name

def build_vtab(vtab_type, method_pointers):
    """
    Create ctypes virtual method table.

    vtab_type: the vtab struct type (typesystem.struct)
    method_pointers: a list of method pointers ([int])
    """
    assert len(method_pointers) == len(vtab_type.fields)

    vtab_ctype = numba.struct(
        [(vtab_name(field_name), field_type)
            for field_name, field_type in vtab_type.fields]).to_ctypes()

    methods = []
    for (method_name, method_pointer), (field_name, field_type) in zip(
                                        method_pointers, vtab_type.fields):
        assert method_name == field_name
        method_type_p = field_type.to_ctypes()
        cmethod = ctypes.cast(ctypes.c_void_p(method_pointer), method_type_p)
        methods.append(cmethod)

    vtab = vtab_ctype(*methods)
    return vtab, vtab_type

#------------------------------------------------------------------------
# Build Extension Type
#------------------------------------------------------------------------

def create_extension(env, py_class, flags):
    """
    Compile an extension class given the NumbaEnvironment and the Python
    class that contains the functions that are to be compiled.
    """
    flags.pop('llvm_module', None)

    ext_type = typesystem.ExtensionType(py_class)
    class_dict = dict(vars(py_class))

    inherit_attributes(ext_type, class_dict)
    process_class_attribute_types(ext_type, class_dict)

    method_pointers, lmethods = compile_extension_methods(
            env, py_class, ext_type, class_dict, flags)
    inject_descriptors(env, py_class, ext_type, class_dict)

    vtab, vtab_type = build_vtab(ext_type.vtab_type, method_pointers)

    logger.debug("struct: %s" % ext_type.attribute_struct)
    logger.debug("ctypes struct: %s" % ext_type.attribute_struct.to_ctypes())
    extension_type = extension_types.create_new_extension_type(
            py_class.__name__, py_class.__bases__, class_dict,
            ext_type, vtab, vtab_type,
            lmethods, method_pointers)
    return extension_type
