"""Modelling my PhD samples."""

import numpy as N
import matplotlib.pyplot as P
import pyFresnelInit
import pyFresnel.finite_well as QW
import pyFresnel.transfer_matrix as TM
from pyFresnel.materials import Material_nk
import pyFresnel.constants as C

##### Modelling the ISBTs

x=0.31
    
#barrier height?
VmeV=835.5*x # (meV)
#effective mass in well?
Mw=0.067 # (relative to Me)
#effective mass in barrier?
Mb=0.067+0.083*x # (relative to Me)
#width of well?
d=6.3e-9 # (m)
#width of barrier?
b=30e-9 # (m)
#doping? 
Ns=12.6 # (1E11cm-2)
#Temperature?
T=15 # (K)
#eps GaAs
eps_b=3.3**2
    
N.set_printoptions(precision=3)
ISBTeps=QW.QW_GUI(VmeV,Mb,Mw,d,Ns,T,b,eps_b,gammaf=0.1,figures=True)
T=300 #K
#Ns*=2
ISBTeps_B=QW.QW_GUI(VmeV,Mb,Mw,d,Ns,T,b,eps_b,gammaf=0.1,figures=True)

##### Modelling the Optical measurments

GaAs=3.3
AlGaAs=3.3

Layer = TM.Layer

structure= [Layer(GaAs,None),
            Layer(AlGaAs,200e-9),
            Layer(GaAs,500e-9),
            Layer(AlGaAs,30e-9)]+ \
            [ISBTeps]*50 + \
            [Layer(GaAs,100e-9),
            Layer(GaAs,5e-9), #should be doped
            Layer(GaAs,40e-9),
            Layer(1.0,None)]

structure_B= [Layer(GaAs,None),
            Layer(AlGaAs,200e-9),
            Layer(GaAs,500e-9),
            Layer(AlGaAs,30e-9)]+ \
            [ISBTeps_B]*50 + \
            [Layer(GaAs,100e-9),
            Layer(GaAs,5e-9), #should be doped
            Layer(GaAs,40e-9),
            Layer(1.0,None)]

pi=N.pi
meV = N.linspace(100,300,500) #meV axis
w = meV*C.e*1e-3/C.hbar # frequency (Hz) (natural = 2*pi*f)
f = w/2/C.pi*1e-12 #frequency (THz) (real)
    
MQW = TM.Filter(
        structure,
        w=w,
        pol='TM',
        theta=pi/4)

MQW_B = TM.Filter(
        structure_B,
        w=w,
        pol='TM',
        theta=pi/4)

########Calculate Reflection/Transmission###
w,R,T=MQW.calculate_R_T(pol='TM')
w,R2,T2=MQW.calculate_R_T(pol='TE')

w,RB,TB=MQW_B.calculate_R_T(pol='TM')
w,R2B,T2B=MQW_B.calculate_R_T(pol='TE')
    
f1=P.figure()
ax1 = P.subplot(111)
ax1.set_title("Sample ccp139/u27066")
#axis = f
#ax1.set_xlabel("Frequency (THz)")
axis = meV
ax1.set_xlabel("Energy (meV)")
ax1.plot(axis,R,label="TM Reflection")
#ax1.plot(axis,T,label="TM Transmission")
ax1.plot(axis,R2,label="TE Reflection")
#ax1.plot(axis,T2,label="TE Transmission")

ax1.plot(axis,RB,label="TM Reflection -300K")
#ax1.plot(axis,TB,label="TM Transmission -300K")
ax1.plot(axis,R2B,label="TE Reflection -300K")
#ax1.plot(axis,T2B,label="TE Transmission -300K")
ax1.legend()

########Calculate E field###################
mod2=lambda a : a*a.conj() #modulus squared
   
z = N.linspace(-1.0e-6,4e-6,1000) #(m)
zaxis = z*1e6 #(um)
fi = 100 #choose index for frequency (this is equiv. to 5.5THz for this script).
    
Efields=MQW.calculate_E(z,pol='TM')
 
Efields2=MQW.calculate_E(z,pol='TE')
""" 
#check TM transmission coefficient
MQW.pol='TE' #this is so we calculate the n2cos(theta2)/(n1cos(theta1)) factor (rather than the n1cos(theta2)/(n2cos(theta1))
print 'TM Transmission at %g THz = ' %(f[fi]*1e-12), MQW._lambda((MQW[0],MQW[-1]))[fi]*(mod2(Efields['Ez'][0,fi])+mod2(Efields['Ex'][0,fi]))
    
#check TE transmission coefficient
print 'TE Transmission at %g THz = ' %(f[fi]*1e-12), MQW._lambda((MQW[0],MQW[-1]))[fi]*mod2(Efields2['Ey'][0,fi])
"""    
############################################

f2 = P.figure()
ax2 = P.subplot(211)
ax2.plot(zaxis,mod2(Efields['Ex'][:,fi]),label="|Ex|**2")
ax2.plot(zaxis,mod2(Efields['Ez'][:,fi]),label="|Ez|**2")
#ax2.plot(zaxis,mod2(Efields['Dz'][:,fi]),label="|Dz|**2")
ax2.plot(zaxis,mod2(Efields2['Ey'][:,fi]),label="|Ey|**2")
ax2.set_xlabel("distance (um)")
ax2.set_ylabel("|E|**2")
ax3 = P.subplot(212,sharex=ax2)
ax3.plot(zaxis,mod2(Efields['Dz'][:,fi]),label="|Dz|**2")
ax2.legend()
ax3.legend()
   
P.show()
            