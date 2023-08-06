"""Material refractive indices for some metals. The data is from Freesnell and 
the initial motivation is that these are the materials need for the filters in
Isotropic_metallic_filters.py which are reproductions of Freesnell's metallic.scm
for testing purposes"""

import numpy as N
from scipy.interpolate import interp1d,splrep,splev
import constants as C

#Sopra data loader
def loadMAT(fname):
    with file(fname) as fobj:
        output=[]
        for line in fobj:
            linelist=line.split('*')
            if linelist[0]=='DATA1':
                output.append(map(float,linelist[2:5])) # data stored as wavelength(nm),n,k
        return N.array(output)
    

##Aluminium
al=N.loadtxt('al.nk',skiprows=2)  #columns =  eV,n,k,R(th=0)
w_axis=al[:,0]*C.e/C.hbar #natural frequency
#al_nk=al[:,1]+1j*al[:,2]
#Al = interp1d(w_axis,al_nk) #basic
#Al = interp1d(w_axis,al[:,1],kind='cubic') # doesn't work.
Alspline_real = splrep(w_axis,al[:,1],s=0)
Alspline_imag = splrep(w_axis,al[:,2],s=0) #library doesn't work with complex numbers?
Al = lambda w: splev(w,Alspline_real,der=0)+1j*splev(w,Alspline_imag,der=0)

"""
import matplotlib.pyplot as P
ax1=P.subplot(111)
ax1.plot(w_axis,al[:,1],label='n real')
ax1.plot(w_axis,al[:,2],label='n imag')
w = N.linspace(1e14,1e17,2000)
ax1.plot(w,Al(w).real,label='n spline real')
ax1.plot(w,Al(w).imag,label='n spline imag')
ax1.set_xscale('log')
#ax1.set_yscale('log')
ax1.legend()
P.show()
"""
"""
## Gold (Au)
au=N.loadtxt('au.nk',skiprows=2)  #columns =  eV,n,k,R(th=0)
w_axis=au[:,0]*C.e/C.hbar #natural frequency
#print 'Au range (um)',C.c*C.pi*2/w_axis[0]*1e6, C.c*C.pi*2/w_axis[-1]*1e6
#au_nk=au[:,1]+1j*au[:,2]
#Au = interp1d(w_axis,au_nk) #basic
#Au = interp1d(w_axis,au_nk,kind='cubic') # doesn't work.
Auspline_real = splrep(w_axis,au[:,1],s=0)
Auspline_imag = splrep(w_axis,au[:,2],s=0) #library doesn't work with complex numbers?
Au = lambda w: splev(w,Auspline_real,der=0)+1j*splev(w,Auspline_imag,der=0)
"""

##Gold (Au) (Sopra)
au2=loadMAT('AU.MAT') 
w_axis=C.c*2*C.pi*1e9/au2[:,0] #natural frequency
#au2_nk=au2[:,1]+1j*au2[:,2]
#Au2 = interp1d(w_axis,au2_nk) #basic
#Au2 = interp1d(w_axis,au2_nk,kind='cubic') # doesn't work.
Au2spline_real = splrep(w_axis[::-1],au2[::-1,1],s=0)
Au2spline_imag = splrep(w_axis[::-1],au2[::-1,2],s=0) #library doesn't work with complex numbers?
Au = lambda w: splev(w,Au2spline_real,der=0)+1j*splev(w,Au2spline_imag,der=0)
    
