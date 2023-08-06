import numpy as np
from numba import *
import math
from math import sqrt, cos
from numba.vectorize import Vectorize, vectorize
import numba

print float_.is_float
print double.is_float

from numba.specialize import mathcalls
print mathcalls.filter_math_funcs(['asinh'])

@numba.export("pymodulo uint32(uint32,uint32)")
def pymodulo(a,b) :
    return a%b




