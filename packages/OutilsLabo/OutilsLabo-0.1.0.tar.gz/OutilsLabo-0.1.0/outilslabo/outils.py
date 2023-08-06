#!/usr/bin/python
# -*- coding: utf-8 -*-

from pylab import *
from numpy import diff,array
from scipy import signal, interpolate
import os


def limit(tab,lo=None,hi=None ,x=0):
    if lo == None:
	try:
        	lo = tab[x][0]
	except:
		lo = tab[0]
	
    if hi == None:
	try:
    		hi = tab[x][-1]
	except:
		hi = tab[-1]

    try:
        return ((tab.T)[tab[x].searchsorted(lo):tab[x].searchsorted(hi)]).T
    except:
        return ((tab.T)[tab.searchsorted(lo):tab.searchsorted(hi)]).T

def sortx(tab):
	return tab.T[lexsort((tab[1],tab[0]))].T
	
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
    #return (x, interpolate.splev(x, tck, der=n))
    return array([x.tolist(), (interpolate.splev(x, tck, der=n)).tolist()])


def find_roots(x, y, delta):
	tmp = (y*y).tolist()
	roots = []

	min_tmp = min(tmp)
	idx = tmp.index(min_tmp)
	while min_tmp <= delta*delta:
		roots.append(x[idx])
		tmp[idx] = 3.*delta*delta

		min_tmp = min(tmp)
		idx = tmp.index(min_tmp)
	
	roots = array(roots)
	roots.sort()
	return roots
		
class polynome:
	def __init__(self,degre):
		self.degre = degre
		self.__name__ = 'Polynome de degre {}'.format(self.degre)
	
	def __call__(self,x,p):
		somme = 0
		for i in range(0,self.degre+1):
			somme += p[i]*x**float(i)
		return somme


def pdfcrop(file_input, file_output=None):
	if file_output is None:
		file_output = file_input
	os.system('pdfcrop {} {}'.format(file_input,file_output))

