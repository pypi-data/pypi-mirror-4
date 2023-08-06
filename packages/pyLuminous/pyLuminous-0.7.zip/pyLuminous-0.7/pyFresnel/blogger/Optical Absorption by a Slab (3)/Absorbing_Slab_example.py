#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# This file is part of pyFresnel.
# Copyright (c) 2012, Robert Steed
# Author: Robert Steed (rjsteed@talk21.com)
# License: GPL
# last modified 18.12.2012
import numpy as N
import Optical_Plate as OP
sqrt=N.sqrt

eps0=8.8541E-12 #Farads/metres -vacuum permittivity.
m_e=9.1094e-31 #Kg - mass of electron
q=1.6022e-19 #C - unit charge.
c=299792458  #m/s - speed of light
pi=N.pi

class material(object):
    """Like a dielectric, plasma, quantum well etc"""
    def __init__(self):
        """This base class has a circular definition for n and epsilon. One 
        function must be overridden in the derived class!"""        
        pass
        
    def epsilon(self):
        return self.n()**2

    def n(self):
        return sqrt(self.epsilon())
        
    def __len__(self):
        pass
        
    def __add__(self,other): # this might not work once we start using the Claussius-Claussis relation!
        """Add two derived instances of classes derived from material"""
        def new_epsilon(self2):
            return self.epsilon()+other.epsilon()
        newmat=material()
        newmat.epsilon=new_epsilon.__get__(newmat,material) # binds function to instance
        return newmat

class Lorentz_model(material):
    """Simple model of an absorbing oscillator / transition.
    Frequencies - whether we use real or natural frequency doesn't matter as long as we are consistant! 
    Remember that there is a difference of 2pi between the two: w=2*pi*f
    Note that normally the equations for the plasma frequency will give a natural frequency but that otherwise
    will be interested in real frequencies."""
    def __init__(self,w,w0,y,wp,f,eps_b):
        #
        #So if these are real frequencies, the plasma frequency must be real too (and the normal equations give a natural value).
        self.w=w
        self.w0=w0
        self.y=y
        self.wp=wp
        self.f=f
        self.eps_b=eps_b
    
    def epsilon(self):
        w,w0,y,wp,f,eps_b=self.w,self.w0,self.y,self.wp,self.f,self.eps_b
        eps=eps_b*(1+wp**2*f/(w0**2-w**2-2j*y*w))
        return eps
        
    @staticmethod   
    def wp(N,meff,eps_b):
        """N (m**-3) charge density
        meff (fraction of m_e) effective mass
        eps_b (unitless) background dielectric"""
        return sqrt(N*q**2/(meff*m_e*eps0*eps_b))
        
        
if __name__=="__main__":
    import pylab as pl
    freq=pl.arange(0,6e12,5e9) #Frequency range (Hz) (REAL)
    #Real vs Natural Frequencies, whether we are using real or natural frequencies is not
    #important for the dielectric constant which is unitless but is important for the
    #calculation of the phase shift which requires a natural frequency.
    L=Lorentz_model(w=freq,w0=2e12,y=15e10,wp=1.6e12,f=1.0,eps_b=1.0)
    #w0 - frequency of transition (Hz) (real)
    #y - broadening of transition (~Half Width Half Maximum) (Hz) (real)
    #wp - Plasma frequency (affects the strength of the transition) (real)
    #f - oscillator strength (also affects the strength of the transition - factor due to quantum mechanics of the transition/oscillator). Can leave at 1.0.
    #eps_b - background dielectric constant.
    
    #Setup optical plate object
    slab=OP.Plate(n1=L.n(),d=5e-6,w=2*pi*freq,theta=pi/4,n0=1.0,n2=1.0) 
    #theta - angle of incidence (rad)
    #d - thickness of plate (m)
    #n0,n2 - refractive indices either side of slab
    
    #
    pl.figure(1,figsize=(7,8))
    THz=freq*1e-12
    ax1=pl.subplot(411)
    ax2=pl.subplot(412, sharex=ax1)
    ax3=pl.subplot(413,sharex=ax1)
    ax4=pl.subplot(414,sharex=ax1)
    #
    ax1.plot(THz,L.epsilon().real,label="epsilon real")
    ax1.plot(THz,L.epsilon().imag,label="epilon imaginary")
    #
    ax2.plot(THz,L.n().real,label="refractive index")
    ax2.plot(THz,L.n().imag,label="kappa")
    #
    ax3.plot(THz,2*(2*pi*freq)*L.n().imag/c,label="absorption coefficient")
    #
    ax4.plot(THz,slab.T_s(),label='Slab Transmission Spol')
    ax4.plot(THz,slab.T_p(),label='Slab Transmission Ppol')
    #
    for ax in ax1,ax2,ax3,ax4: # As might be obvious from my code, there are many possible equations for the position of the peak and it depends upon which quantity you are interested in as well..
        ax.axvline(L.w0*1e-12,color='r') #w0
        #ax.axvline(sqrt(L.w0**2-L.y**2),color='b') #damping shifted peak
        ax.axvline(sqrt(L.w0**2+L.wp**2*L.f)*1e-12,color='r')
        #ax.axvline(sqrt(L.w0**2+L.wp**2),color='g')
        #ax.axvline(sqrt(L.w0**2-L.y**2+L.wp**2*L.f),color='b')
        #ax.axvline(sqrt(L.w0**2-L.y**2+L.wp**2),color='k')
    ax1.legend()
    ax2.legend()
    ax3.legend()
    ax4.legend()
    ax1.set_title("Various properties of an example Lorentzian Oscillator")
    ax4.set_xlabel("Frequency (real) (THz)")
    ax4.set_xlim((1,6))
    pl.subplots_adjust(left=0.11, bottom=0.08, right=0.95, top=0.95,
                wspace=None, hspace=None)
    
    pl.show()
    
    
