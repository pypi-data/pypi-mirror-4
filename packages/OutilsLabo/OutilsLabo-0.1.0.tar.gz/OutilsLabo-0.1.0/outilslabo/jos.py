#!/usr/bin/python
# -*- coding: utf-8 -*-
from pylab import *
from scipy.optimize import leastsq
import sys
import derivative as div
import scipy.constants as C
import scipy.odr as odr

#   Retourne un string avec le NOM de la la variable d'entrée
def namestr(obj, namespace=globals()):  
    return [name for name in namespace if namespace[name] is obj]

#   Fonctions mathématiques courantes

def coth(x):
    return 1/tanh(x)

def tnlN(x,p):  # Bruit dans une jonction tunnelle p0*x*coth(p1*x)+p2
    w=nonzero(x)
    ret=0.*x+(p[2]+p[0]/p[1])
    ret[w]=p[0]*x[w]*coth(x[w]*p[1])+p[2]
    return ret


#   Fonctions pour graphiques

def exa(file): # Load un fichier csv fait au EXA
    return loadtxt(file,unpack=True,skiprows=44,delimiter=',')

def pna(file): # Load un fichier csv fait au PNA
    return loadtxt(file,unpack=True,skiprows=8,delimiter=',',comments='END')


def fp(file,x=0,y=1,label='_file_',format='',**kwargs):
    if type(file)==type('str'):
        if label=='_file_':
            label=file
        tmp=loadtxt(file,unpack=True,**kwargs)
        plot(tmp[x],tmp[y],format,label=label)
    else:
        if label=='_file_':
            label='x=='+namestr(file)[0]+'[%d]'%x+' , '+'y=='+namestr(file)[0]+'[%d]'%y
        plot(file[x],file[y],format,label=label)

def fD1(file,x=0,y=1,label='_file_',format='',**kwargs):
    if type(file)==type('str'):
        if label=='_file_':
            label=file
        tmp=loadtxt(file,unpack=True,**kwargs)
    else:
        tmp=file
        if label=='_file_':
            label='fD1(x=='+namestr(file)[0]+'[%d]'%x+' , '+'y=='+namestr(file)[0]+'[%d])'%y
    dx,dy=div.D1(tmp[x],tmp[y])
    plot(dx,dy,format,label=label)

def fDf(file,x=0,y=1,label='_file_',format='',sigma=5,**kwargs):
    if type(file)==type('str'):
        if label=='_file_':
            label=file
        tmp=loadtxt(file,unpack=True,**kwargs)
    else:
        tmp=file
        if label=='_file_':
            label='fDf(x=='+namestr(file)[0]+'[%d]'%x+' , '+'y=='+namestr(file)[0]+'[%d])'%y
    dx,dy=div.Dfilter(tmp[x],tmp[y],sigma)
    plot(dx,dy,format,label=label)
   

def ifit(x,y,p0,f,fullo=1,yerr=1,xerr=1):
    """ 
    """
    def _residuals(p,data,x,yerr):
        err=(data-f(x,p))/yerr
        return err
    lsq=leastsq(_residuals,p0,args=(y,x,yerr),full_output=fullo)
    dt=lsq[0]
    cv=lsq[1]
    sdcv=sqrt(diag(cv))
    corrM=cv/sdcv/sdcv[:,None]
    chi2=sum(((y-f(x,dt))/yerr)**2)
    chi2r=chi2/(len(y)-len(p0))
    err=sdcv*sqrt(chi2r)

    class fitreturn:
        def __init__(self,tab):
            self.tab=tab
            self.beta=tab[0]
            self.chi2r=chi2r
            self.err=err
        def __getitem__(self,b):
            return self.tab[b]
        def __call__(self):
            return self.tab
        def __repr__(self):
            return self.tab.__repr__()
        
    ret=fitreturn([dt,err,chi2r,corrM,lsq[2]['nfev'],lsq[3]])
    return ret
    # [0:'Parameters', 1:'Error On Parameters', 2:'Reduced Chi2', 3:'Correlation Matrix', 4:'# Iterations', 5:'Verbose'] ; ret.beta = _[0]

def odrfit(_x,_y,xerr,yerr,p0,f,silent=False):
    model=odr.Model(f)
    mydata=odr.Data(_x,y=_y,we=yerr,wd=xerr)
    myodr=odr.ODR(mydata,model,p0)
    myoutput=myodr.run()
    cv=myoutput.cov_beta
    sdcv=sqrt(diag(cv))
    corrM=cv/sdcv/sdcv[:,None]
    chi2=sum(((_y-f(myoutput.beta,_x))/yerr)**2)
    chi2r=chi2/(len(_y)-len(p0))
    err=myoutput.sd_beta
    setattr(myoutput,'chi2r',chi2r)
    setattr(myoutput,'err',err)
    setattr(myoutput,'corrM',corrM)
    if not silent:
        myoutput.pprint()
        print 'Reduced chi2 is %.10g\n'%chi2r
    
    class fitreturn:
        def __init__(self,myoutput):
            self.tab=[myoutput.beta,myoutput.err,myoutput.chi2r,myoutput.corrM,myoutput.cov_beta]
            self.beta=myoutput.beta
            self.chi2r=myoutput.chi2r
            self.err=myoutput.err      
            self.corrM=myoutput.corrM
            self.cov_beta=myoutput.cov_beta
            self.myoutput=myoutput
        def __getitem__(self,b):
            return self.tab[b]
        def __call__(self):
            return self.tab
        def __repr__(self):
            myoutput.pprint()
            return 'Reduced chi2 is %.10g\n'%chi2r

    return fitreturn(myoutput)

def iodrfit(_x,_y,p0,f,xerr=1,yerr=1,silent=False):
    def fct(_p0,__x):
        return f(__x,_p0)
    return odrfit(_x,_y,xerr,yerr,p0,fct,silent)

    

def TfitConv(x,y,R,p0=[-1e-3,0.2,-0.006],f=tnlN):
    """
    """ 
    c=[]
    try:
        for i in arange(0,size(x)/2,1):
            j=size(x)-i
            b=ifit(x[i:j],y[i:j],p0,f)
            T=C.e*R/(2*C.k*1e5*b[0][1])
            if T<0:
                T=T*(-1)
            c.append([i,T])
    except ValueError:
       pass 
    return array(c).transpose()

def sortNParray(array,column=0,isT=True):
    if isT:
        tmp=array.T
        return tmp[tmp[:,column].argsort()].T
    else:
        return array[array[:,column].argsort()]



def limit(tab,lo,hi ,x=0):
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

    

def ifind(array,value,many=False): # index find
    idx=(np.abs(array-value)).argmin()
    return idx

#def irange(tab,min,max):
#    return(ifind)






