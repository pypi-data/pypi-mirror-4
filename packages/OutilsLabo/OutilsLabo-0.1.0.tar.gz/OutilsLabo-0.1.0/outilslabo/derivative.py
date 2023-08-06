#!/usr/bin/python
# -*- coding: utf-8 -*-

from numpy import diff,array
from scipy.misc import central_diff_weights
from scipy import signal, interpolate
from scipy.ndimage import filters

def D1(x, y, axis=-1):
    """ Simplest numerical derivative of order 1
        returns x', dy/dx(x')
    """
    dx = diff(x,axis=axis)
    dy = diff(y,axis=axis)
    return x[:-1]+dx/2, dy/dx

def Dn(x, y, Np, ndiv=1, mode='reflect', cval=0.):
    """ central numerical derivative using Np points of order ndiv
        (Np>1 and odd), using convolution 
        Data needs to be equally spaced in x
        can use mode= 'nearest'. 'wrap', 'reflect', 'constant'
        cval is for 'constant'
        returns x', d^n y/dx^n(x')
    """
    dx = x[1]-x[0]
    kernel = central_diff_weights(Np,ndiv=ndiv)
    dy = filters.correlate1d(y, kernel, mode=mode, cval=cval)
    return x, dy/dx**ndiv

def Dfilter(x, y, sigma, axis=-1, mode='reflect', cval=0.):
    """ gaussian filter of size sigma and order 1
        Data should be equally space for filter to make sense
        (sigma in units of dx)
        can use mode= 'nearest'. 'wrap', 'reflect', 'constant'
        cval is for 'constant'
    """
    dx = x[1]-x[0]
    yf = filters.gaussian_filter1d(y, sigma, axis=axis, mode=mode, cval=cval, order=1)
    return x, yf/dx
    #return D1(x, yf, axis=axis)

def Dspline(x, y, sigma=None, s=None, k=3, n=1):
    """ derivative using splines
         k is spline oder (3: cubic, 1 <= k <= 5)
         sigma is standard error of y (needed for smoothing)
         s is smoothing factor (chi^2 <= s)
        returns x', d^n y/dx^n(x')
          n needs to be <= k
        To check the initial data use n=0
         plot(x,y,'.-')
         plot(*Dspline(x,y,s=1,n=0))
    """
    global tck
    extra={}
    if sigma != None:
       extra['w']=1./sigma
    tck = interpolate.splrep(x, y, k=k, s=s, **extra)
    return (x, interpolate.splev(x, tck, der=n))

# for 2d look at filters.sobel and filers.prewitt
# other filters: filters.uniform_filter1d
#                signal.spline_filter signal.cspline1d, signal.bspline
#                 signal is for fast transform. Assumes equally spaced points
