#!/usr/bin/python
# -*- coding: utf-8 -*-

import dmath as dm
import dclass as dc
import numpy as np

#__all__ = [acos,acosh,asin,asinh,atan,atanh,cos,cosh,exp,log,log10,sin,sinh,sqrt,tan,tanh]
_acos = np.frompyfunc(dm.acos,1,1)
_acosh = np.frompyfunc(dm.acosh,1,1)
_asin = np.frompyfunc(dm.asin,1,1)
_asinh = np.frompyfunc(dm.asinh,1,1)
_atan = np.frompyfunc(dm.atan,1,1)
_atanh = np.frompyfunc(dm.atanh,1,1)
_cos = np.frompyfunc(dm.cos,1,1)
_cosh = np.frompyfunc(dm.cosh,1,1)
_exp = np.frompyfunc(dm.exp,1,1)
_log = np.frompyfunc(dm.log,2,1)
_log10 = np.frompyfunc(dm.log10,1,1)
_sin = np.frompyfunc(dm.sin,1,1)
_sinh = np.frompyfunc(dm.sinh,1,1)
_sqrt = np.frompyfunc(dm.sqrt,1,1)
_tan = np.frompyfunc(dm.tan,1,1)
_tanh = np.frompyfunc(dm.tanh,1,1)


_isinstance_array = np.frompyfunc(isinstance,2,1)

def isdonnee(x):
	return np.any(_isinstance_array(x,dc.donnee))


def acos(x):
	"""acos(x)

	Return the arc cosine of x."""
	
	if np.any(_isinstance_array(x,dc.donnee)):
		return _acos(x)
	else:
		return np.acos(x)

def acosh(x):
	"""acosh(x)

	Return the hyperbolic arccosine of x."""

	if np.any(_isinstance_array(x,dc.donnee)):
		return _acosh(x)
	else:
		return np.acosh(x)

def asin(x):
	"""asin(x)

	Return the arc sine of x."""
	
	if np.any(_isinstance_array(x,dc.donnee)):
		return _asin(x)
	else:
		return np.asin(x)

def asinh(x):
	"""asinh(x)

	Return the hyperbolic arc sine of x."""
	
	if np.any(_isinstance_array(x,dc.donnee)):
		return _asinh(x)
	else:
		return np.asinh(x)

def atan(x):
	"""atan(x)
	
	Return the arc tangent of x."""
	
	if np.any(_isinstance_array(x,dc.donnee)):
		return _atan(x)
	else:
		return np.atan(x)

def atanh(x):
	"""atanh(x)

	Return the hyperbolic arc tangent of x."""
	
	if np.any(_isinstance_array(x,dc.donnee)):
		return _atanh(x)
	else:
		return np.atanh(x)

def cos(x):
	"""cos(x)

	Return the cosine of x."""

	if np.any(_isinstance_array(x,dc.donnee)):
		return _cos(x)
	else:
		return np.cos(x)

def cosh(x):
	"""cosh(x)
	
	Return the hyperbolic cosine of x."""

	if np.any(_isinstance_array(x,dc.donnee)):
		return _cosh(x)
	else:
		return np.cosh(x)

def exp(x):
	"""exp(x)

	Return the exponential value e**x."""

	if np.any(_isinstance_array(x,dc.donnee)):
		return _exp(x)
	else:
		return np.exp(x)

def log(x, base=None):
	"""log(x)

	Return the natural logarithm of x."""

	if np.any(_isinstance_array(x,dc.donnee)):
		return _log(x,base)
	else:
		if base is None:
			return np.log(x)
		else:
			return np.divide(np.log(x),np.log(base))

def log10(x):
	"""log10(x)

	Return the base-10 logarithm of x."""
	
	if np.any(_isinstance_array(x,dc.donnee)):
		return _log10(x)
	else:
		return np.log10(x)

def sin(x):
	"""sin(x)

	Return the sine of x."""

	if np.any(_isinstance_array(x,dc.donnee)):
		return _sin(x)
	else:
		return np.sin(x)

def sinh(x):
	"""sinh(x)

	Return the hyperbolic sine of x."""
	
	if np.any(_isinstance_array(x,dc.donnee)):
		return _sinh(x)
	else:
		return np.sinh(x)

def sqrt(x):
	"""sqrt(x)

	Return the square root of x."""
	
	if np.any(_isinstance_array(x,dc.donnee)):
		return _sqrt(x)
	else:
		return np.sqrt(x)

def tan(x):
	"""tan(x)

	Return the tangent of x."""

	if np.any(_isinstance_array(x,dc.donnee)):
		return _tan(x)
	else:
		return np.tan(x)
		return self.__repr__()

def tanh(x):
	"""tanh(x)

	Return the hyperbolic tangent of x."""
	
	if np.any(_isinstance_array(x,dc.donnee)):
		return _tanh(x)
	else:
		return np.tanh(x)

