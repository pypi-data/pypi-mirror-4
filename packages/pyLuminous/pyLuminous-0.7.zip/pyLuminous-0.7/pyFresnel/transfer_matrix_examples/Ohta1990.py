"""Trying to replicate some graphs from Ohta's 1990 paper "Matrix Formulism for
calculation of electric field intensity of light in stratified multilayered films"

"""

import pyFresnelInit
import pyFresnel.transfer_matrix as TM
Layer=TM.Layer
import numpy as N
import matplotlib.pyplot as P
import pyFresnel.constants as C
c=C.c #speed of light
pi=C.pi
mod2=lambda a : a*a.conj() #modulus squared
##

v=1000 #cm-1 - wavenumber
w=v*100*c*2*pi #Hz (natural) - frequency

#Fig. 2 Angular depedence of the electric field intensity Fz(z) at the surface 
#of the metal for the case of reflection absorption spectroscopy.
fig2 = P.figure()
fig2ax1 = fig2.add_subplot(111)
fig2ax1.set_title("fig.2 RA")
angles = N.linspace(0.0,89.9,300.0)

metalsurface = TM.Filter(
                [Layer(1.0,None),
                Layer(1.0,0.01e-6),
                Layer(3.0+30.0j,None)],
                w=w,
                pol='TM',
                theta=angles*pi/180.0)

z=N.array([0.01])*1e-6

n1s=[1.0,1.5,1.5+0.5j] #different values for first layer's refractive index
labels=["(a) n1 =1.0","(b) n1 = 1.5","(c) n1 = 1.5+0.5j"]
for n1,label in zip(n1s,labels):
    metalsurface[1]._n=n1 #this is a bit of a hack to change the value of first layer's refractive index.
    Efields=metalsurface.calculate_E(z)
    fig2ax1.plot(angles,mod2(Efields['Ez'][0,:]),label=label )
metalsurface[1]._n=1.0 #return refractive index to it's original state.

fig2ax1.set_xlabel("Incident angle (degrees)")
fig2ax1.set_ylabel("Field Intensity Fz(z)")
fig2ax1.legend()

###Fig.3 Depth profile of the electric field intensity Fz(z) at the incident angle
###of 75deg for the case of reflection-absorption spectroscopy.
fig3 = P.figure()
fig3ax1 = fig3.add_subplot(111)
fig3ax1.set_title("fig.3 RA")

z=N.linspace(-0.01,0.02,500) #um
zcalc = (0.01-z)*1e-6 # the figure in the paper uses a different definition for the z-axis. Origin starts at ij=01 interface
metalsurface.theta=N.array([75])*pi/180.0

for n1,label in zip(n1s,labels):
    metalsurface[1]._n=n1 #this is a bit of a hack to change the value of first layer's refractive index.
    Efields=metalsurface.calculate_E(zcalc)
    fig3ax1.plot(z,mod2(Efields['Ez'][:,0]),label=label)
metalsurface[1]._n=1.0 #return refractive index to it's original state.

fig3ax1.set_xlabel("distance from metal interface (um)")
fig3ax1.set_ylabel("Field Intensity Fz(z)")
fig3ax1.legend()


###Fig.4. Angular dependence of the electric field intensity Fz(z) at the surface
##of the metal for the case of surface electromagnetix wave spectroscopy

angles = N.linspace(24.5,24.7,3000.0)

SEW = TM.Filter(
                [Layer(2.4,None),
                Layer(1.0,45.76e-6),
                Layer(1.0,0.01e-6),
                Layer(3.0+30.0j,None)],
                w=w,
                pol='TM',
                theta=angles*pi/180.0)

fig4 = P.figure()
fig4ax1 = fig4.add_subplot(111)
fig4ax1.set_title("fig.4 SAW")

z=N.array([0.005])*1e-6

n2s=[1.0,1.5,1.5+0.5j] #different values for second layer's refractive index
ds=[45.76,44.22,38.6] #different thicknesses for the first layer
labels=["(a) n2 =1.0, d1=45.76um","(b) n2 = 1.5, d1=44.22um","(c) n2 = 1.5+0.5j, d1=38.60"]
for n2,d,label in zip(n2s,ds,labels):
    SEW[2]._n=n2 #this is a bit of a hack to change the value of second layer's refractive index.
    SEW[1].d=d*1e-6 #this is a bit of a hack to change the value of first layer's thickness.
    Efields=SEW.calculate_E(z)
    fig4ax1.plot(angles,mod2(Efields['Ez'][0,:]),label=label )
SEW[2]._n=1.0 #return refractive index to it's original state.
SEW[1].d=45.76e-6 #return thickness to it's original state.

fig4ax1.set_xlabel("Incident angle (degrees)")
fig4ax1.set_ylabel("Field Intensity Fz(z)")
fig4ax1.legend()

###Fig.5 Depth profile of the electric field intensity Fz(z) at the various incident angles
##for the case of surface electromagnetic wave spectroscopy.
fig5 = P.figure()
fig5ax1 = fig5.add_subplot(111)
fig5ax1.set_title("fig.5 SAW")

z=N.linspace(-20.0,60.0,500) #um # the figure in the paper uses a different definition for the z-axis. Origin starts at ij=01 interface

SEWangles=[24.622,24.626,24.619] # optimum angles for each structures surface wave.
for n2,d,angle,label in zip(n2s,ds,SEWangles,labels):
    SEW[2]._n=n2 #this is a bit of a hack to change the value of second layer's refractive index.
    SEW[1].d=d*1e-6 #this is a bit of a hack to change the value of first layer's thickness.
    SEW.theta=N.array([angle])*pi/180.0
    zcalc = sum([layer.d for layer in SEW[1:-1]])-z*1e-6 # the figure in the paper uses a different definition for the z-axis. Origin starts at ij=01 interface
    Efields=SEW.calculate_E(zcalc)
    fig5ax1.plot(z,mod2(Efields['Ez'][:,0]),label=label)
SEW[2]._n=1.0 #return refractive index to it's original state.
SEW[1].d=45.76e-6 #return thickness to it's original state.

fig5ax1.set_xlabel("distance from metal interface (um)")
fig5ax1.set_ylabel("Field Intensity Fz(z)")
fig5ax1.legend()

###Fig.7. Angular dependence of the electric field intensity Fz(z) at the surface
##of the metal for the case of metal overlay ATR spectroscopy
fig7 = P.figure()
fig7ax1 = fig7.add_subplot(111)
fig7ax1.set_title("fig.7 MOATR")
angles = N.linspace(0.0,89.9,300.0)

MOATR = TM.Filter(
                [Layer(4.0,None),
                Layer(1.0,0.01e-6),
                Layer(3.0+30.0j,None)],
                w=w,
                pol='TM',
                theta=angles*pi/180.0)

z=N.array([0.01])*1e-6

n1s=[1.0,1.5,1.5+0.5j] #different values for first layer's refractive index
labels=["(a) n1 =1.0","(b) n1 = 1.5","(c) n1 = 1.5+0.5j"]
for n1,label in zip(n1s,labels):
    MOATR[1]._n=n1 #this is a bit of a hack to change the value of first layer's refractive index.
    Efields=MOATR.calculate_E(z)
    fig7ax1.plot(angles,mod2(Efields['Ez'][0,:]),label=label )
MOATR[1]._n=1.0 #return refractive index to it's original state.

fig7ax1.set_xlabel("Incident angle (degrees)")
fig7ax1.set_ylabel("Field Intensity Fz(z)")
fig7ax1.legend()

###Fig.3 Depth profile of the electric field intensity Fz(z) at the incident angle
###of 75deg for the case of reflection-absorption spectroscopy.
fig8 = P.figure()
fig8ax1 = fig8.add_subplot(111)
fig8ax1.set_title("fig.8 MOATR")

z=N.linspace(-0.01,0.02,500) #um
zcalc = (0.01-z)*1e-6 # the figure in the paper uses a different definition for the z-axis. Origin starts at ij=01 interface
MOATR.theta=N.array([75])*pi/180.0

for n1,label in zip(n1s,labels):
    MOATR[1]._n=n1 #this is a bit of a hack to change the value of first layer's refractive index.
    Efields=MOATR.calculate_E(zcalc)
    fig8ax1.plot(z,mod2(Efields['Ez'][:,0]),label=label)
MOATR[1]._n=1.0 #return refractive index to it's original state.

fig8ax1.set_xlabel("distance from metal interface (um)")
fig8ax1.set_ylabel("Field Intensity Fz(z)")
fig8ax1.legend()

P.show()