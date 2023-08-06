#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# This file is part of pyFresnel.
# Copyright (c) 2012, Robert Steed
# Author: Robert Steed (rjsteed@talk21.com)
# License: GPL
# last modified 18.12.2012
"""None too clever class for calculating the effective dielectric tensor of a set
of layers"""


class EffectiveMedium():
    def __init__(self,layers):
        """layers is a list of tuples. Each tuple is (epszz, epsxx, thickness (m))
        Currently it is up to you to ensure that each layer is using the same frequency
        axis!"""
        self.layers=layers
        self.Ltot=sum([L for epszz,epsxx,L in layers])

    def eps_xx(self):
        #sum L*epsxx
        return sum([epsxx*L for epszz,epsxx,L in self.layers])/self.Ltot

    def eps_zz(self):
        #inverse(sum L/epszz)
        return self.Ltot/sum([L/epszz for epszz,epsxx,L in self.layers])
        


if __name__=="__main__":
    """Comparing effective medium to a thin film model"""
    import Transfer_Matrix as TM
    from material_class import Lorentz_model
    from Uniaxial_Plate2 import Plate as aniso_Plate
    import matplotlib.pyplot as pl
    import numpy as N
    pi=N.pi
    
    freq=N.arange(0,6e12,5e9) #Frequency range (Hz) (REAL)
    w=2*pi*freq
    #Real vs Natural Frequencies, whether we are using real or natural frequencies is not
    #important for the dielectric constant which is unitless but is important for the
    #calculation of the phase shift which requires a natural frequency.
    
    theta=pi/4
    
    eps_b=1.0
    
    L=Lorentz_model(w=freq,w0=2e12,y=15e10,wp=1.6e12,f=1.0,eps_b=eps_b)
    #w0 - frequency of transition (Hz) (real)
    #y - broadening of transition (~Half Width Half Maximum) (Hz) (real)
    #wp - Plasma frequency (affects the strength of the transition) (real)
    #f - oscillator strength (also affects the strength of the transition - factor due to quantum mechanics of the transition/oscillator). Can leave at 1.0.
    #eps_b - background dielectric constant.
    
    #Setup Transfer Matrix
    filterlist = [TM.Layer(eps_b,None)]+\
        [TM.Layer(L.epsilon(),5e-6), #dielectric constant, thickness (m)
        TM.Layer(eps_b,40e-6)]*4+\
        [TM.Layer(eps_b,None)]
    #
    f1 = TM.filter(filterlist,
                w=w, #Frequency (natural) (Hz)
                pol='TM', #polarisation: either 'TM' or 'TE'
                theta=theta*180/pi) # angle of incidence (degrees)
    #
    w,R,T=f1.calculate_R_T()
    #
    # Effective Medium Model
    filterlist2=[(layer.eps,layer.eps,layer.d) for layer in filterlist[1:-1]]
    dtotal=sum([layer[2] for layer in filterlist2])
    #
    EM=EffectiveMedium(filterlist2)
    aniso_slab=aniso_Plate(EM.eps_zz(),EM.eps_xx(),dtotal,w,theta,eps_b=eps_b)
    
    ##################

    pl.figure(1) #,figsize=(7,8))
    THz=freq*1e-12
    ax1=pl.subplot(111)
    #
    ax1.plot(THz,R,label="reflection (TM)")
    ax1.plot(THz,T,label="transmission (TM)")
    #
    ax1.plot(THz,aniso_slab.R_p(),label="eff. medium: reflection (TM)")
    ax1.plot(THz,aniso_slab.T_p(),label="eff. medium: transmission (TM)")
    #
    ax1.legend()
    ax1.set_title("A Uniaxial Transfer Matrix")
    ax1.set_xlabel("Frequency (real) (THz)")
    ax1.set_xlim((1,6))
    #
    pl.show()