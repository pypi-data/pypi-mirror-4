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
#import transfer_matrix as TM
from numpy import sqrt

class EffectiveMedium_eps():
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
            
    def n_xx(self):
        return sqrt(self.eps_xx())
        
    def n_zz(self):
        return sqrt(self.eps_zz())
        


class EffectiveMedium():
    def __init__(self,layers,w=None):
        """layers is a list of tuples where each tuple is either 
        (nzz, nxx, thickness (m)), 
        (nzz, thickness (m)) or 
        a Layer object from transfer_matrix.py. 
        Currently it is up to you to ensure that each layer is using the same 
        frequency axis! Also if you use Layer objects you should supply 'w' when
        initialising the class."""
        self.layers=layers
        self.w=w

    def _thickness(self,layer):
        if hasattr(layer,'d'):
            d=layer.d
        elif hasattr(layer, '__getitem__'):
            d=layer[-1]
        else:
            raise Exception("Can not determine the thickness of the layer")
        return d
    
    def Ltot(self):
        return sum([self._thickness(layer) for layer in self.layers])

    def eps_xx(self):
        #sum L*epsxx
        Ltot=self.Ltot()
        #
        def epsxx(layer):
            if type(layer)==tuple:
                if len(layer)==2:
                    epsxx= layer[0]**2
                elif len(layer)==3:
                    epsxx= layer[1]**2
                else:
                    raise Exception("layer tuple is the wrong length.")
            elif hasattr(layer,'n'):
                epsxx= layer.n(self.w)**2
            else:
                raise Exception("Can not find a refractive index (xx) for layer")
            return epsxx
        #
        return sum([epsxx(layer)*self._thickness(layer) for layer in self.layers])/Ltot

    def eps_zz(self):
        #inverse(sum L/epszz)
        Ltot=self.Ltot()
        #
        def epszz(layer):
            if type(layer)==tuple:
                if len(layer)==2:
                    epszz= layer[0]**2
                elif len(layer)==3:
                    epszz= layer[0]**2
                else:
                    raise Exception("layer tuple is the wrong length.")
            elif hasattr(layer,'nzz'):
                epszz= layer.nzz(self.w)**2
            elif hasattr(layer,'n'):
                epszz= layer.n(self.w)**2
            else:
                raise Exception("Can not find a refractive index (zz) for layer")
            return epszz
        #
        return Ltot/sum([self._thickness(layer)/epszz(layer) for layer in self.layers])
            
            
    def n_xx(self):
        return sqrt(self.eps_xx())
        
    def n_zz(self):
        return sqrt(self.eps_zz())


if __name__=="__main__":
    """Comparing effective medium to a thin film model"""
    import transfer_matrix as TM
    from materials import LorentzModel
    from uniaxial_plate2 import AnisoPlate #, AnisoPlate_eps
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
    
    L=LorentzModel(w=freq,w0=2e12,y=15e10,wp=1.6e12,f=1.0,eps_b=eps_b)
    #w0 - frequency of transition (Hz) (real)
    #y - broadening of transition (~Half Width Half Maximum) (Hz) (real)
    #wp - Plasma frequency (affects the strength of the transition) (real)
    #f - oscillator strength (also affects the strength of the transition - factor due to quantum mechanics of the transition/oscillator). Can leave at 1.0.
    #eps_b - background dielectric constant.
    
    #Setup Transfer Matrix
    filterlist = [TM.Layer_eps(eps_b,None)]+\
        [TM.Layer_eps(L.epsilon(),5e-6), #dielectric constant, thickness (m)
        TM.Layer_eps(eps_b,40e-6)]*4+\
        [TM.Layer_eps(eps_b,None)]
    #
    f1 = TM.Filter(filterlist,
                w=w, #Frequency (natural) (Hz)
                pol='TM', #polarisation: either 'TM' or 'TE'
                theta=theta) # angle of incidence (radians)
    #
    w,R,T=f1.calculate_R_T()
    #
    # Effective Medium Model
    """
    filterlist2=[(layer.eps,layer.eps,layer.d) for layer in filterlist[1:-1]]
    dtotal=sum([layer[2] for layer in filterlist2])
    #
    EM=EffectiveMedium_eps(filterlist2)
    anisoslab=AnisoPlate_eps(EM.eps_zz(),EM.eps_xx(),dtotal,w,theta,eps_b=eps_b)
    """
    # Effective Medium Model2
    #
    #filterlist3=[(layer.n(w),layer.d) for layer in filterlist[1:-1]]
    EM2=EffectiveMedium(filterlist[1:-1],w)
    #anisoslab=AnisoPlate_eps(EM2.eps_zz(),EM2.eps_xx(),dtotal,w,theta,eps_b=eps_b)
    anisoslab=AnisoPlate(EM2.n_xx(),EM2.n_zz(),EM2.Ltot(),w,theta,n_b=sqrt(eps_b))
    
    ##################

    pl.figure(1) #,figsize=(7,8))
    THz=freq*1e-12
    ax1=pl.subplot(111)
    #
    ax1.plot(THz,R,label="reflection (TM)")
    ax1.plot(THz,T,label="transmission (TM)")
    #
    ax1.plot(THz,anisoslab.R_p(),label="eff. medium: reflection (TM)")
    ax1.plot(THz,anisoslab.T_p(),label="eff. medium: transmission (TM)")
    #
    ax1.legend()
    ax1.set_title("A Uniaxial Transfer Matrix")
    ax1.set_xlabel("Frequency (real) (THz)")
    ax1.set_xlim((1,6))
    #
    pl.show()