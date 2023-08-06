#!/usr/bin/python
# -*- coding: utf-8 -*-

import sympy as sp
import donnee as d
from math import sqrt

class func_gen:
	"""
	Prend une expression symbolique 'expr' et une liste de variables
	'var' pour retourner une fonction numérique de ces variables
	ainsi que son calcul d'erreur.

	Chaque élément de 'var' doit être un symbol.
		ex:
		var[0] = sympy.Symbol('x')
	"""

	def __init__(self,expr,var):
		self.expr = expr
		self.var = var
		self.func_valeur = sp.lambdify(var,expr)
		self.calcul_derivees()

	def calcul_derivees(self):
		self.derivees = []
		for i in range(0,len(self.var)):
			self.derivees.append(sp.lambdify(self.var,sp.diff(self.expr,self.var[i])))

	def __call__(self,*args):
		if len(args) != len(self.var):
			print 'Erreur: Cette fonction est définie à {} arguments'.format(len(self.var))
		else:
			
			delta_carre = 0.
			for i in range(0,len(self.var)):
				delta_carre += (self.derivees[i](*d.valeurs(args))*d.incertitudes(args)[i])**2.
			return d.donnee(self.func_valeur(*d.valeurs(args)),sqrt(delta_carre))


	
