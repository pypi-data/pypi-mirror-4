#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# This file is part of pyFresnel.
# Copyright (c) 2012, Robert Steed
# Author: Robert Steed (rjsteed@talk21.com)
# License: GPL
# last modified 18.12.2012
import pyFresnelInit
from pyFresnel.effective_medium import EffectiveMedium_eps
from pyFresnel.optical_plate import Plate as Plate0
from pyFresnel.uniaxial_plate2 import AnisoPlate_eps
from pyFresnel.materials import QW_ISBT,Material_nk
from pyFresnel.fresnel import Interface

import numpy as N
import matplotlib.pyplot as pl
pi=N.pi
sqrt=N.sqrt; cos=N.cos
c=299792458  #m/s - speed of light

####### "experiment"
theta=pi/4
f=N.arange(1e10,4e12,1e9)
w=2*pi*f

####### Define refractive indices
#over-engineered but I hope to have a frequency dependent refractive index soon
well=Material_nk(3.585) # refractive index of GaAs
barrier=Material_nk(3.585) # refractive index of AlGaAs

####### Define ISBT
w0=1.1e12*2*pi # frequency of transition (natural)
y=1e11*2*pi # broadening of transition (Hz) (natural)
f12=0.96 # oscillator strength
Lqw=47e-9 # (m) width of quantum well.
N2D=1.28 # 2d population difference of quantum well (1E11cm**-2).
N2D*=1E11 # convert to cm**-2
N=N2D/Lqw/100.0 # 3D density (cm**-3) this is a very simple model. No effective lengths for ISBT.
eps_well=well.epsilon() # dielectric constant near to w0?
wp=QW_ISBT.wp(N,eps_well,meff=0.067) # calculating plasma frequency (natural)

ISBT1=QW_ISBT(w,w0,y,f12,wp,well.epsilon())

QW0=Plate0(ISBT1.n(),Lqw,w,theta,n0=barrier.n(),n2=barrier.n())

eps_zz=ISBT1.epsilon()
#eps_xx=eps_zz
eps_xx=well.epsilon()
QW=AnisoPlate_eps(eps_xx,eps_zz,Lqw,w,theta,eps_b=barrier.epsilon())

######### Effective Medium
"""Going to check whether I get the same results for various thicknesses of effective
media"""
    
Lcomposite=2000e-9 #Lqw #(m) total thickness of structure
n=1.0
Lbarrier=Lcomposite - n*Lqw #(m) thickness that is barrier

layers0=[(barrier.epsilon(),barrier.epsilon(),Lbarrier),
        (ISBT1.epsilon(),ISBT1.epsilon(),n*Lqw)]
    
EM0=EffectiveMedium_eps(layers0) # non uniaxial dielectric for ISBT
EMQW0=AnisoPlate_eps(EM0.eps_xx(),EM0.eps_zz(),Lcomposite,w,theta,eps_b=barrier.epsilon())

layers=[(barrier.epsilon(),barrier.epsilon(),Lbarrier),
        (ISBT1.epsilon(),well.epsilon(),n*Lqw)]
    
EM=EffectiveMedium_eps(layers) # uniaxial dielectric for ISBT
EMQW=AnisoPlate_eps(EM.eps_xx(),EM.eps_zz(),Lcomposite,w,theta,eps_b=barrier.epsilon())        
    
######### 

ax=pl.subplot(111)
ax.set_title("Absorption of slabs with a (isotropic,anisotropic) transitions\nand testing Effective Medium Theory\n(Intersubband Transitions of Quantum Wells)")
#plots have been roughly normalised

ax.axvline(w0/2/pi)#line for w0
ax.axvline(sqrt(w0**2-y**2)/2/pi)#line for sqrt(w0**2 - y**2)
#ax.plot(f,ISBT1.epsilon().imag*0.0003,label="imaginary epsilon")
#ax.plot(f,w*ISBT1.epsilon().imag/well.n().real/c*Lqw/cos(theta),label="simplified absorption over layer length") #simple absorption for quantum well = w * eps'' / n_background /c
#ax.plot(f,2*w*ISBT1.n().imag/c*Lqw/cos(theta),label="proper absorption over layer length")#absorption in a quantum well 'medium'
ax.plot(f,1-QW0.T_p(),label="absorption of isotropic transition") #absorption in a quantum well slab, thickness Lqw
ax.plot(f,1-QW.T_p(),label="absorption of an anisotopic transition") #absorption in a quantum well slab, thickness Lqw
ax.plot(f,1-EMQW0.T_p(),'--',label="Effective medium of slabs with isotropic absorption") #absorption in a quantum well slab, thickness Lqw
ax.plot(f,1-EMQW.T_p(),'--',label="Effective medium of slabs with anisotropic absorption") #absorption in a quantum well slab, thickness Lqw
#ax.axvline(sqrt(w0**2+wp**2)/2/pi)#line for sqrt(w0**2 + wp**2) (using Lqw not Leff)
#ax.axvline(sqrt(w0**2-y**2+wp**2)/2/pi)#line for sqrt(w0**2 - y**2 + wp**2)
ax.axvline(sqrt(w0**2+f12*wp**2)/2/pi)#line for sqrt(w0**2 + f12*wp**2) (using Lqw not Leff)
ax.axvline(sqrt(w0**2-y**2+f12*wp**2)/2/pi)#line for sqrt(w0**2 - y**2 + f12*wp**2)

ax.set_ylim([0,0.05])
ax.set_xlabel("Frequency (THz)")
ax.set_ylabel("1 - Transmittance")
ax.legend()
pl.show()