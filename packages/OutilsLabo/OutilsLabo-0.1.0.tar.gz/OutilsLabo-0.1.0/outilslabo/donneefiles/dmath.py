#!/usr/bin/python
# -*- coding: utf-8 -*-

import math
from dclass import *


def acos(x):
	"""acos(x)

	Return the arc cosine of x."""
	
	x = donnee(x)
	return donnee(math.acos(x.v),x.i/math.sqrt(1.-x.v**2.))


def acosh(x):
	"""acosh(x)

	Return the hyperbolic arccosine of x."""

	x = donnee(x)
	return donnee(math.acosh(x.v),x.i/math.sqrt(x.v**2.-1.))


def asin(x):
	"""asin(x)

	Return the arc sine of x."""
	
	x = donnee(x)
	return donnee(math.asin(x.v),x.i/math.sqrt(1.-x.v**2.))


def asinh(x):
	"""asinh(x)

	Return the hyperbolic arc sine of x."""
	
	x = donnee(x)
	return donnee(math.asinh(x.v),x.i/math.sqrt(x.v**2.+1.))


def atan(x):
	"""atan(x)
	
	Return the arc tangent of x."""
	
	x = donnee(x)
	return donnee(math.atan(x.v),x.i/(x.v**2.+1.))


def atanh(x):
	"""atanh(x)

	Return the hyperbolic arc tangent of x."""
	
	x = donnee(x)
	return donnee(math.atanh(x.v),x.i/(1.-x.v**2.))


def cos(x):
	"""cos(x)

	Return the cosine of x."""

	x = donnee(x)
	return donnee(math.cos(x.v),math.sin(x.v)*x.i)


def cosh(x):
	"""cosh(x)
	
	Return the hyperbolic cosine of x."""

	x = donnee(x)
	return donnee(math.cosh(x.v),math.sinh(x.v)*x.i) 


def exp(x):
	"""exp(x)

	Return the exponential value e**x."""

	x = donnee(x)
	return donnee(math.exp(x.v),math.exp(x.v)*x.i)


def log(x, base=None):
	"""log(x)

	Return the natural logarithm of x."""

	x = donnee(x)
	if base is not None:
		return donnee(math.log(x)/math.log(base),x.i/(x.v*math.log(base)))
	return donnee(math.log(x.v),x.i/x.v)


def log10(x):
	"""log10(x)

	Return the base-10 logarithm of x."""
	
	x = donnee(x)
	return donnee(math.log10(x.v),x.i/(x.v*math.log(10.)))


def sin(x):
	"""sin(x)

	Return the sine of x."""

	x = donnee(x)
	return donnee(math.sin(x.v),math.cos(x.v)*x.i)


def sinh(x):
	"""sinh(x)

	Return the hyperbolic sine of x."""
	
	x = donnee(x)
	return donnee(math.sinh(x.v),math.cosh(x.v)*x.i)


def sqrt(x):
	"""sqrt(x)

	Return the square root of x."""
	
	x = donnee(x)
	return donnee(math.sqrt(x.v),x.i/(2.*math.sqrt(x.v)))


def tan(x):
	"""tan(x)

	Return the tangent of x."""

	x = donnee(x)
	return donnee(math.tan(x.v),x.i/((math.cos(x.v))**2.))


def tanh(x):
	"""tanh(x)

	Return the hyperbolic tangent of x."""
	
	x = donnee(x)
	return donnee(math.tanh(x.v),x.i/((math.cosh(x.v))**2.))

#__all__ = [acos,acosh,asin,asinh,atan,atanh,cos,cosh,exp,log,log10,sin,sinh,sqrt,tan,tanh]
