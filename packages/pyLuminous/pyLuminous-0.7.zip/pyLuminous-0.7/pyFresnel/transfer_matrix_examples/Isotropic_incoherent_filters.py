"""Testing the isotropic part of the incoherent transfer matrix class using the 
incoherent tests from Freesnell. See the Freesnell website for details.
Any differences are due to the interpolation of the HDPE refractive index data
which is very sparse for the few interesting absorption features."""

import pyFresnelInit
import pyFresnel.incoherent_transfer_matrix as TM
from metals_nk import Al,Au
Layer=TM.Layer
import numpy as N
import matplotlib.pyplot as P
pi=N.pi
c=299792458  #m/s - speed of light
from scipy.interpolate import interp1d,splrep,splev

def creatematerial(data):
    """takes an array of column data: 
    spectral axis, n, k
    and returns a function that spline interoplates over the
    refractive index data
    """    
    axis=data[:,0]
    nkspline_real = splrep(axis,data[:,1],s=0)
    nkspline_imag = splrep(axis,data[:,2],s=0) #library doesn't work with complex numbers?
    return lambda axis: splev(axis,nkspline_real,der=0)+1j*splev(axis,nkspline_imag,der=0)

### HDPE refractive index
HDPEn= 1.54+0.002j

class HDPELayer(Layer):
    def __init__(self,d,coh=True):
        """HDPE refractive index data between 2.5 - 15um wavelength"""
        data=N.loadtxt('HDPE2.nk',skiprows=1)
        data[:,0]=c*2*pi*1e6/data[:,0] #convert from um to w (natural Hz)
        self._nkspline_real = splrep(data[::-1,0],data[::-1,1],s=0) #need increasing w for spline procedure to work
        self._nkspline_imag = splrep(data[::-1,0],data[::-1,2],s=0)        
        #self.n = lambda axis: splev(axis,self._nkspline_real,der=0)+1j*splev(axis,self._nkspline_imag,der=0)
        self.d = d
        self.coh=coh
        self._n ='HDPE'#data  #for repr()
        
    def n(self,w):
        return splev(w,self._nkspline_real,der=0)+1j*splev(w,self._nkspline_imag,der=0)
"""
P.figure()
ax0=P.subplot(111)
ax0.set_title("Polythene refractive index")
lamda = N.logspace(N.log10(3e-6),N.log10(15e-6),1200) # (m) wavelength
w = 2*pi*c/lamda # (Hz) frequency (natural)
HDPE=HDPELayer(None)
axis = lamda #N.log10(lamda)
ax0.plot(axis,HDPE.n(w).real,label="n")
ax0.plot(axis,HDPE.n(w).imag,label="k")
data=N.loadtxt('HDPE2.nk',skiprows=1)
ax0.scatter(data[:,0]*1e-6,data[:,1],label="n data")
ax0.scatter(data[:,0]*1e-6,data[:,2],label="k data")
ax0.set_xlabel("log(wavelength(m))")
ax0.set_ylabel("Transmittance")
ax0.legend()
"""
### Polythene Filters
#As modelled by Freesnell - PE-3x14-co
#lamda = N.linspace(3e-6,15e-6,200) # (m) wavelength
lamda = N.logspace(N.log10(3e-6),N.log10(15e-6),1200) # (m) wavelength
w = 2*pi*c/lamda # (Hz) frequency (natural)

P.figure()
ax1 = P.subplot(111)
ax1.set_title("14um Polyethylene Films")

for repeats in 3,:#1,2,3:
    polythenefltr = TM.IncoherentFilter(
            [Layer(1.0,None)]+\
            [Layer(1.0,1e-3),
            HDPELayer(14e-6)]*repeats+\
            [Layer(1.0,None)],
            w=w,
            pol='TM',
            theta=4.0*pi/180)

    w,R,T=polythenefltr.calculate_R_T()
    ax1.plot(N.log10(lamda),T,label="%d film(s) (coherent)" %repeats)

    #incoherent
    for i in range(1,repeats*2,2):
        polythenefltr[i].coh=False
    w,Rincoh,Tincoh=polythenefltr.calculate_R_T()
    ax1.plot(N.log10(lamda),Tincoh,label="%d film(s) incoherent" %repeats)

ax1.set_ylim([0.0,1.])
ax1.set_xlabel("log(wavelength(m))")
ax1.set_ylabel("Transmittance")
ax1.legend(loc=8)

P.show()


