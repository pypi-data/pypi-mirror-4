"""This script can be used to model a microcavity containing QWs with Intersubband
transitions that strongly couple to the cavity leading to an anticrossing phenomena
known as a polariton.

Structure is GaAs - AlGaAs."""

import numpy as N
#import matplotlib
import matplotlib.pyplot as P
import pyFresnelInit
import pyFresnel.transfer_matrix as TM
#import pyFresnel.incoherent_transfer_matrix as ITM
import pyFresnel.layer_types as layer_types
import pyFresnel.finite_well as finite_well
from pyFresnel.transfer_matrix import Layer
#from scipy.interpolate import interp1d,splrep,splev
import pyFresnel.constants as C
c = C.c
pi = C.pi
print "libraries imported"

##Define structure - 
#number of wells,barrier and cladding thicknesses, top surface mirror and bottom
#surface (partial) mirror. Define material refractive indices/dielectric constants

nGaAs = 3.4
nAlGaAs = 3.4
GaAs_THz = layer_types.GaAs_THz
Gold_THz = layer_types.Gold_THz

numQWs = 40 #number of repeats
lQW = 10 #(nm)
barrier = 20 #(nm)

cladding_bottom = 30 #(nm)
cladding_top = 50 #(nm)

bottom_mirror_N = 200 #partial mirror doping (3D) (1e18cm**-3)
bottom_mirror_d = 150 #partial mirror thickness (nm)

##Define ISBTs
#There are two approaches. We can define the transition within its (uniaxial) layer
#and then the final transition will exhibit a depolarisation shift - 
#w0'**2 = w0**2 + wp**2 where wp is the plasma frequency. However to calculate the
#plasma frequency, we should remember that the effective thickness of the oscillator
#is given by 0.6 the thickness of the QW. Alternatively, we can calculate the 
#dielectric constant of the effective medium that includes the QWs and their 
#separating barriers. This approach is better for fitting to real data since the
#the inverse of the dielectric constant can consist of a sum of oscillators with
#approximately the same frequencies as those observed in the data. Also, this approach
#is useful when doing more advanced modelling of intersubband transitions and their
#mutual couplings since it naturally leads to an effective medium formulism.

#Approach 1 - use layer_types.QW_ISBT
w0= 2*pi*c/17.0e-6 #Transition frequency (natural frequency (Hz))
f12= 0.96 #Oscillator Strength, 0.96 is typical for the lowest intersubband transition of a QW.
y= w0*0.15 #Transition broadening (natural frequency (Hz))
N2D= 16e11 # cm**-2

eps_well_w0= 3.4**2 # the background dielectric constant of the well layer (GaAs) at the frequency of the transition (we're assuming that it doesn't vary too fast)
meff= 0.067 # the relative effective mass of conduction band electrons in GaAs
leff= 0.6*lQW # the effective thickness of the transition, 0.6lQW is typical for the lowest intersubband transition of a QW.
wp=layer_types.QW_ISBT.wp(N2D/(leff*1e2*1e-9),eps_well_w0,meff=0.067)

isbt1 = layer_types.QW_ISBT(w0,y,f12,wp,nGaAs**2,lQW*1e-9,coh=True)

structure1 =   [Layer(nGaAs,None),
                GaAs_THz(bottom_mirror_N,bottom_mirror_d*1e-9), # bottom_mirror_N
                Layer(nGaAs,cladding_bottom*1e-9)] +\
               [isbt1,
                Layer(nAlGaAs,barrier*1e-9)]*numQWs +\
               [Layer(nGaAs,cladding_top*1e-9),
                #Gold_THz(100e-9),
                Layer(1.0,None)]

#Define angles - mapping between exterior and interior angles.
#The high refractive index of GaAs makes it difficult to access all internal angles
#of incidence. The usual solution is to polish the edge facets at an angle and here
#the high refractive index becomes an advantage for the angular resolution of an
#experiment, since small changes in the internal angles are caused by large changes
#in external angle.

#theta = internal angle of incidence to microcavity (rad)
#alpha = angle of facet polish wrt substrate plane (degrees)
#angle = external angle of incidence (degrees)

def internaltheta(angle,alpha,n):
    sin = N.sin;arcsin = N.arcsin # get sin,asin function from numpy library
    d2r=pi/180.0 #degrees to rads
    return alpha*d2r - arcsin(sin(angle*d2r)/n)

#if we provide an array of the nGaAs wrt w, then should we be able to calculate 
#the response of each frequency wrt to its unique angle of incidence?

alpha = 50 #(degrees)

## Ouput (graphs)
fig1 = P.figure(1)
ax1 = fig1.add_subplot(111)

#wavelength = N.linspace(2,50,400) # define wavelengths range (um)
#w = 2*pi*c/wavelength*1e6 # calculate natural frequencies range (Hz)

v = N.linspace(1,50,1000) # define frequency (THz)
w = v*2*pi*1e12 # calculate natural frequencies range (Hz)

angles = N.linspace(70,-70,10) # define external angles of measurement (degrees)
thetas = internaltheta(angles,alpha,nGaAs) # calculate internal angles of incidence (rad)

#angles = N.linspace(20,80,15) # define internal angles (degrees)
#thetas = angles*pi/180.0 # internal angles (radians)

#create TM object

microcavity = TM.Filter(structure1,w,'TM',theta=thetas[0])

for offset,(theta,angle) in enumerate(zip(thetas,angles)):
    microcavity.theta=theta
    w,R,T=microcavity.calculate_R_T()
    ax1.plot(v,R+0.3*offset,label='%.3g ext. = %.3g int.' %(angle,theta*180/pi))
    #ax1.plot(v,R+0.3*offset,label='%.3g deg.' %(angle))

#ax1.set_xlabel('wavelength (um)')
ax1.set_xlabel('frequency (THz)')
ax1.set_ylabel('Reflectivity')
ax1.legend()
P.show()







