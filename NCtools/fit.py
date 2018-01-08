# -*- coding: utf-8 -*-
"""
data = np.array([1.5, 3.15, 4.965, 6.9615, 9.1577, 11.5734, 14.2308, 17.1538, 20.3692, 23.9061, 27.7968, 32.0764, 36.7841, 41.9625, 47.6587])
x = np.arange(data.shape[0])

#Fit data to a function defined like this:
def f(x): return b*np.power(a,x) + c

#Init parameters:
a = Parameter()
b = Parameter()
c = Parameter()

#And fit the function parameters to the data
print(fit(f, [a,b,c], data, x))

y=f(np.arange(0,data.shape[0]))

plt.plot(data,'.')
plt.plot(y, '-')
"""

import numpy as np
from scipy import optimize
#import matplotlib.pyplot as plt

class Parameter(object):

    '''
    Acts as a numpy.float64 in all aspects thought of. 
    But with the the set method added so it acts as a mutable float.
    '''
#    value = np.float64()
    
    def __init__(self, value=1.0):
        self.value = np.float64(value)

    def set(self, value):
            self.value = np.float64(value)

#    def __call__(self):
#            return self.value

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return str(self.value)

    def __add__(self, other):
        return self.value.__add__(other)
    def __sub__ (self, other):
        return self.value.__sub__(other)
    def __mul__ (self, other):
        return self.value.__mul__(other)
#    def __div__ (self, other):
#        return self.value.__div__(other)
    def __mod__ (self, other):
        return self.value.__mod__(other)
    def __divmod__ (self, other):
        return self.value.__divmod__(other)
    def __pow__ (self, other):
        return self.value.__pow__(other)
    def __lshift__ (self, other):
        return self.value.__lshift__(other)
    def __rshift__ (self, other):
        return self.value.__rshift__(other)
    def __and__ (self, other):
        return self.value.__and__(other)
    def __xor__ (self, other):
        return self.value.__xor__(other)
    def __or__ (self, other):
        return self.value.__or__(other)
#
    def __radd__(self, other):
        return self.value.__add__(other)
    def __rsub__ (self, other):
        return self.value.__sub__(other)
    def __rmul__ (self, other):
        return self.value.__mul__(other)
#    def __rdiv__ (self, other):
#        return self.value.__div__(other)
    def __rmod__ (self, other):
        return self.value.__mod__(other)
    def __rdivmod__ (self, other):
        return self.value.__divmod__(other)
    def __rpow__ (self, other):
        return self.value.__pow__(other)
    def __rlshift__ (self, other):
        return self.value.__lshift__(other)
    def __rrshift__ (self, other):
        return self.value.__rshift__(other)
    def __rand__ (self, other):
        return self.value.__and__(other)
    def __rxor__ (self, other):
        return self.value.__xor__(other)
    def __ror__ (self, other):      
        return self.value.__or__(other)

    def __neg__ (self):
        return self.value.__neg__()
    def __pos__ (self):
        return self.value.__pos__()
    def __abs__ (self):
        return self.value.__abs__()
    def __invert__ (self):
        return self.value.__invert__()
#    def __complex__ (self):
#        return self.value.__complex__()
    def __int__ (self):
        return self.value.__int__()
#    def __long__ (self):
#        return self.value.__long__()
    def __float__ (self):
        return self.value.__float__()
#    def __oct__ (self):
#        return self.value.__oct__()
#    def __hex__ (self):
#        return self.value.__hex__()

        
def fit(function, parameters, y, x = None, **kwargs):
    if not isinstance(y, np.ndarray):
        y = np.array(y)
    def f(params):
        i = 0
        for p in parameters:
            p.set(params[i])
            i += 1
        return y - np.array(function(x)).astype(np.float64)

    if x is None: x = np.arange(y.shape[0])
    p = [param for param in parameters]
    return optimize.least_squares(f, p, **kwargs)




