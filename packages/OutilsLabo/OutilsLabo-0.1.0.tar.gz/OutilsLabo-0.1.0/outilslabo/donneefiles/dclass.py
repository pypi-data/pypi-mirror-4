#!/usr/bin/python
# -*- coding: utf-8 -*-

from pylab import *

class donnee(object):
	def __init__(self,valeur,incertitude = 0.):
		if isinstance(valeur,donnee):
			self.v = valeur.v
			self.i = valeur.i
		else:
			self.v = valeur
			self.i = abs(incertitude)

	def __del__(self):
		del self.v
		del self.i

	def __str__(self):
		if self.v == 0. or self.i == 0.:
			return '{0} ± {1:0.1g} '.format(self.v,self.i)
		else:
			arrondi = int(floor(log10(abs(self.v))))-int(floor(log10(self.i)))+1
			return '{1:0.{0}g} ± {2:0.1g} '.format(arrondi,self.v,self.i)
		

#	def __str__(self):
#		return self.__repr__()

	def __repr__(self):
		return '{} ± {}'.format(self.v,self.i)

	def __gt__(self,other):
		other = donnee(other)
		if self.v-self.i > other.v+other.i:
			return True
		else:
			return False
	
	def __ge__(self,other):
		other = donnee(other)
		if self.__eq__(other) or self.__gt__(other):
			return True
		else:
			return False

	def __lt__(self,other):
		other = donnee(other)
		if self.v+self.i < other.v-other.i:
			return True
		else:
			return False
	
	def __le__(self,other):
		other = donnee(other)
		if self.__eq__(other) or self.__lt__(other):
			return True
		else:
			return False
		
	def __ne__(self,other):
		other = donnee(other)
		if self.__lt__(other) or self.__gt__(other):
			return True
		else:
			return False
	
	def __eq__(self,other):
		other = donnee(other)
		if self.v-self.i <= other.v+other.i and self.v+self.i >= other.v-other.i:
			return True
		elif self.v+self.i >= other.v-other.i and self.v-self.i <= other.v+other.i:
			return True
		else:
			return False

		
	def __add__(self,other):
		other = donnee(other)
		return donnee(self.v+other.v,sqrt(self.i**2.+other.i**2.)) 

	def __radd__(self,other):
		other = donnee(other)
		return other.__add__(self)

	def __sub__(self,other):
		other = donnee(other)
		return donnee(self.v-other.v,sqrt(self.i**2.+other.i**2.)) 

	def __rsub__(self,other):
		other = donnee(other)
		return other.__sub__(self)

	def __mul__(self,other):
		other = donnee(other)
		return donnee(self.v*other.v,sqrt((self.v*other.i)**2.+(other.v*self.i)**2.))

	def __rmul__(self,other):
		other = donnee(other)
		return other.__mul__(self)

	def __div__(self,other):
		other = donnee(other)
		v = self.v/other.v
		i = sqrt((v*self.i/self.v)**2. + (v*other.i/other.v)**2.)
		return donnee(v,i)

	def __rdiv__(self,other):
		other = donnee(other)
		return other.__div__(self)

	def __pow__(self,power):
		return donnee(self.v**power,power*(self.v**(power-1.)))

	def __neg__(self):
		return donnee(-self.v,self.i)

	def __pos__(self):
		return donnee(+self.v,self.i)

	def __abs__(self):
		return donnee(abs(self.v),self.i)

	def __int__(self):
		return int(self.v)

	def __float__(self):
		return float(self.v)


def darray(tabv,tabi):
	assert len(tabv) == len(tabi)
	tabd = []
	for i in range(0,len(tabv)):
		tabd.append(donnee(tabv[i],tabi[i]))
	return array(tabd)


def _valeurs(x):
	return float(donnee(x).v)

_valeurs_array = np.frompyfunc(_valeurs,1,1)

def valeurs(x):
	return array(_valeurs_array(x).tolist())

def _incertitudes(x):
	return float(donnee(x).i)

_incertitudes_array = np.frompyfunc(_incertitudes,1,1)

def incertitudes(x):
	return array(_incertitudes_array(x).tolist())


