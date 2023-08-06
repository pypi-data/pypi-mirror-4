#!/usr/bin/python
# -*- coding: utf-8 -*-

from pylab import *
from labfit import fit
import donnee as d
#from scipy.special import wofz
from outils import limit

imag_i = 0.+1.j

def gaussienne(x,p):
	return abs(float(p[2])*exp(-(x-float(p[0]))**2./(2.*float(p[1])**2.)))

def lorentzienne(x,p):
	return abs(float(p[2])/(1. + ((x-float(p[0]))/(0.5*float(p[1])))**2.))


class melange:
	def __init__(self,prop):
		self.prop = prop
	
	def __call__(self,x,p):
		return self.prop*gaussienne(x,p) + (1.-self.prop)*lorentzienne(x,p)

#def voigt(x,p):
#	'''Voigt profile V(x,[x0,sigma,gamma,A]), which is a convolution of a Gaussian G(x,x0,sigma)
#	and a Lorentzian L(x,x0,gamma)'''
#	x0 = p[0]
#	sigma = p[1]
#	gamma = p[2]
#	z = (x + imag_i*gamma)/(sigma*sqrt(2.))
#	w = wofz(z)
#	return p[3]*real(w)


class peak:
	def __init__(self,p,f=lorentzienne):
		if isinstance(p,peak):
			self.p = p.p
			self.f = p.f
		else:
			self.p = p
			if isinstance(f,float):
				self.f = melange(f)
			else:
				self.f = f
		
	
	def __call__(self,x,p=None):
		if p is None:
			return self.f(x,self.p)
		else:
			return self.f(x,p)

	def __getitem__(self,i):
		return self.p[i]

	def __add__(self,other):
		return peaks([self,other])

	def __str__(self):
		return '{}'.format(self.p)

def _topeak(tab):
	return peak(tab)


class peaks:
	def __init__(self,list_of_peaks):
		if isinstance(list_of_peaks,peaks):
			self._lop = list_of_peaks._lop
		elif isinstance(list_of_peaks,peak):
			self._lop = [list_of_peaks]
		else:
			self._lop = list_of_peaks

		# Liste des paramètres
		self.p = []
		for pk in self._lop:
			self.p += d.valeurs(pk.p).tolist()
		
		self.__name__ = 'Test'

	
	def __call__(self,x,p=None):
		s = 0.
		if p is None:
			#for pk in self._lop:
			#	s += pk(x)
			for i in range(0,len(self._lop)):
				s += self._lop[i](x)
			return s
		else:
			q = self._separate(p)
			for i in range(0,len(self._lop)):
				s += self._lop[i](x,q[i])
			return s

	def _separate(self,p):
		q = []
		for i in range(0,len(self._lop)):
			q.append(p[len(self._lop[i].p)*i:len(self._lop[i].p)*(i+1)])
		return q

	def update(self,p,err = None):
		q = self._separate(p)
		if err is not None:
			dq = self._separate(err)
		for i in range(0,len(q)):
			if err is None:
				self._lop[i].p = q[i]
			else:
				self._lop[i].p = d.darray(q[i],dq[i])

	def __add__(self,other):
		other = peaks(other)
		return peaks(self._lop + other._lop)

	def __getitem__(self,i):
		return self._lop[i]

	def __len__(self):
		return len(self._lop)
	
	def __str__(self, numstart=0):
		string = ''
		for i in range(len(self._lop)):
			string += 'Peak {} = {}\n'.format(i+1+numstart,self._lop[i].__str__())
		return string




class peakfit(fit):
	def __init__(self,x,y,pks,xerr=None,yerr=None,lo=None,hi=None,verbose=True):
		self.peaks = peaks(pks)
		self.subfits = []

		if xerr is None:
			xerr = [1.]*len(x)
		if yerr is None:
			yerr = [1.]*len(y)
		self.xy = limit(array([x,y,xerr,yerr]),lo,hi)

		fit.__init__(self,self.xy[0],self.xy[1],self.peaks.p,self.peaks,fullo=1,xerr=self.xy[2],yerr=self.xy[3],verbose=False)

		self.leastsq()
		self.peaks.update(self.para,self.err)

		# Retour aux versions non limitées (pour éventuels subfits)
		self.x = x
		self.y = y
		self.xerr = xerr
		self.yerr = yerr
		
		if verbose:
			print self


	def __call__(self,x=None):
		if x is None:
			x = self.xFit
		res = self.peaks(x)
		for subfit in self.subfits:
			res += subfit(x)
		return res

	def diff(self):
		return self.y - self(self.x)

	def plotpeaks(self,x=None,scale=1.,fmt='k-'):
		if x is None:
			x = self.xFit
		for p in self.peaks:
			plot(x,p(x)*scale,fmt)
		for subfit in self.subfits:
			subfit.plotpeaks(x,scale,fmt)

	def __getitem__(self,i):
		return self.peaks[i]

	def __len__(self):
		return len(self.peaks)

	def __str__(self,title=True,startnum=0):
		st = ''
		num = startnum
		if title:
			st += '\n--- FIT ON PEAKS ---\n\n'
		st += self.peaks.__str__(num)
		num += len(self.peaks)
		if len(self.subfits) > 0:
			st += '\nSubfits:\n'
			for subfit in self.subfits:
				st += subfit.__str__(title=False,startnum=num)
				num += len(subfit.peaks)
				st += '\n'
		return st
	
	def addsubfit(self,pks,xerr=1,yerr=1,lo=None,hi=None,verbose=True):
		self.subfits.append(peakfit(self.x,self.y-self.peaks(self.x),pks,1,1,lo,hi,False))
		if verbose:
			print self 


		



