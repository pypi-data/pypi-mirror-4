==========
OutilsLabo
==========

Le paquet OutilsLabo apporte des outils utiles lorsque l'on traite des
données obtenues en laboratoire. Il est principalement composé du module
labfit.py qui permet d'effectuer une régression sur les données avec
l'algorithme Least squares ou ODR, du module peakfit.py qui permet de 
situer la position, l'amplitude et la largeur de pics gaussiens, 
lorentziens ou autre et du module donnee.py qui permet de traiter une
donnée et son incertitude comme un seul objet. D'autres outils, comme
des outils de dérivation, sont aussi fournis.


Module labfit
=============

La classe 'fit' crée un objet contenant deux méthodes de fit, soient
fit.leastsq et fit.odr qui renvoient toutes deux le résultat dans
fit.para avec comme erreurs fit.err. Si l'option verbose est activée
(activée par défaut), le fit imprime à l'écran des valeurs importantes
(dont la matrice de corrélation et chi^2).

Elle s'utilise comme suit::

	def Fonction(x,P):
		return 	La_fonction_de_la_variable_x_et_du_tableau_de_paramètres_p

	a = fit(ValeursDeX, ValeursDeY, ParamètresInitiaux, Fonction, xerr=ErreursEnX, yerr=ErreursEnY)
	a.leastsq() OU a.odr()

Aussi, appeler l'objet de 'fit' correspond à appeler la fonction avec
les paramètres stockés dans fit.para (paramètres initiaux au paramètres
de fit)
* a(x) est absolument équivalent à Fonction(x,a.para)

Aussi, on peut aller chercher directement les paramètres du fit en
considérant l'objet comme un tableau:
* a[i] est absolument équivalent à a.para[i]

Les classes 'lsqfit' et 'odrfit' sont absolument identiques à la classe
'fit' (elles héritent de toutes ses méthodes et variables), sauf qu'elle
performent la régression au moment de l'initialisation. Ainsi::
	def Fonction(x,P):
		return La_fonction_de_la_variable_x_et_du_tableau_de_paramètres_p

	a = odrfit(ValeursDeX, ValeursDeY, ParamètresInitiaux, Fonction, xerr=ErreursEnX, yerr=ErreursEnY)


Module peakfit
==============

Cette section est vide pour l'instant


Module donnee
=============

Cette section est vide pour l'instant


Contributors
============

Jean Olivier Simoneau, Christian Lupien
