#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# This file is part of pyFresnel.
# Copyright (c) 2012, Robert Steed
# Author: Robert Steed (rjsteed@talk21.com)
# License: GPL
# last modified 18.12.2012
"""Modelling the depolarisation shift by treating the ISBTs as a thin uniaxial dielectric 
slab. This class includes the Fresnel equations and assumes that the initial and final
media are the same."""

import numpy as N
sin,arcsin,cos,arccos,exp,sqrt=N.sin,N.arcsin,N.cos,N.arccos,N.exp,N.sqrt
#from Fresnel_equations import interface
c=299792458  #m/s - speed of light

class Plate():
    def __init__(self,eps_zz,eps_xx,d,w,theta,eps_b=1.0):
        self.epsb=eps_b #dielectric constant of surounding medium
        self.epszz=eps_zz #dielectric constant of plate perp to interfaces
        self.epsxx=eps_xx #dielectric constant of plate parallel to interfaces
        self.d=d #thickness of plate (m)
        self.w=w #natural frequency (Hz)
        self.theta=theta #angle of incidence (rad)
        
    def _shared(self,pol):
        """pol is 'p' or 's'"""
        epsb=self.epsb; nb=sqrt(epsb)
        epsxx=self.epsxx; nxx=sqrt(epsxx)
        epszz=self.epszz; #nzz=sqrt(epszz)
        d=self.d; w=self.w; theta=self.theta
        #
        K=w/c
        k0z=nb*K*cos(theta)        
        #k0x=nb*K*sin(theta)
        if pol=='p':
            k1z=nxx*K*sqrt(1-epsb*sin(theta)**2/epszz)
        elif pol=='s':
            k1z=K*sqrt(epsxx-epsb*sin(theta)**2)
        delta=k1z*d
        return delta,k0z,k1z
    
    def r_s(self):
        delta,k0z,k1z=self._shared(pol='s')
        Lambda=k1z/k0z
        r01=(1-Lambda)/(1+Lambda)
        exp2delta=exp(2j*delta)
        r_s=r01*(1-exp2delta)/(1-r01**2*exp2delta)
        return r_s        
    
    def r_p(self):
        epsxx=self.epsxx; epsb=self.epsb; #epszz=self.epszz; 
        delta,k0z,k1z=self._shared(pol='p')
        Lambda=epsb*k1z/(epsxx*k0z)
        r01=(1-Lambda)/(1+Lambda)
        exp2delta=exp(2j*delta)
        r_p=r01*(1-exp2delta)/(1-r01**2*exp2delta)
        return r_p  
    
    def t_s(self):
        delta,k0z,k1z=self._shared(pol='s')
        #
        t_s= 1.0/(cos(delta) - 1j*sin(delta)*(k0z**2+k1z**2)/(2*k0z*k1z))
        return t_s  
        
    def t_p(self):
        delta,k0z,k1z=self._shared(pol='p')
        epsxx=self.epsxx; epsb=self.epsb #epszz=self.epszz;
        #
        t_p= 1.0/(cos(delta) - 1j*sin(delta)*((epsxx*k0z)**2+(epsb*k1z)**2)/(2*epsb*epsxx*k0z*k1z) )
        return t_p
    
    def _modsq(self,a):
        if hasattr(a,"conjugate"):
            return a*a.conjugate()
        else:
            return a*a
            
    def R_s(self):
        r_s=self.r_s()
        return self._modsq(r_s)
            
    def R_p(self):
        r_p=self.r_p()
        return self._modsq(r_p)
    
    def T_s(self):
        t_s=self.t_s()
        return self._modsq(t_s)
    
    def T_p(self):
        t_p=self.t_p()
        return self._modsq(t_p)
        
if __name__=="__main__":
    from Optical_Plate import Plate as Plate0
    from material_class import QW_ISBT,material_nk
    #from Fresnel_equations import interface

    import numpy as N
    import matplotlib.pyplot as pl
    pi=N.pi
    sqrt=N.sqrt; cos=N.cos
    c=299792458  #m/s - speed of light


    ####### "experiment"
    theta=pi/4
    f=N.arange(1e10,4e12,1e10)
    w=2*pi*f

    ####### Define refractive indices
    #over-engineered but I hope to have a frequency dependent refractive index soon
    well=material_nk(3.585) # refractive index of GaAs
    barrier=material_nk(3.585) # refractive index of AlGaAs
    
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
    
    def nsimplified(eps):
        return well.n()+1j*eps.imag/(2*well.n().real)
    QWsimplified=Plate0(nsimplified(ISBT1.epsilon()),Lqw,w,theta,n0=barrier.n(),n2=barrier.n())
     
    eps_zz=ISBT1.epsilon()
    #eps_xx=eps_zz
    eps_xx=well.epsilon()
    QW=Plate(eps_zz,eps_xx,Lqw,w,theta,eps_b=barrier.epsilon())
    
    #########
    
    ax=pl.subplot(111)
    #plots have been roughly normalised
    
    ax.axvline(w0/2/pi)#line for w0
    ax.axvline(sqrt(w0**2-y**2)/2/pi)#line for sqrt(w0**2 - y**2)
    ax.plot(f,ISBT1.epsilon().imag*0.0003,label="imaginary epsilon")
    ax.plot(f,w*ISBT1.epsilon().imag/well.n().real/c*Lqw/cos(theta),label="simplified absorption over layer length") #simple absorption for quantum well = w * eps'' / n_background /c
    ax.plot(f,2*w*ISBT1.n().imag/c*Lqw/cos(theta),label="proper absorption over layer length")#absorption in a quantum well 'medium'
    ax.plot(f,1-QWsimplified.T_p(),label="simplified dielectric, absorption in a quantum well slab, thickness Lqw")#absorption of a quantum well 'medium' using simplified dielectric constant
    ax.plot(f,1-QW0.T_p(),label="absorption in a quantum well slab, thickness Lqw") #absorption in a quantum well slab, thickness Lqw
    ax.plot(f,1-QW.T_p(),label="absorption in an anisotopic quantum well slab, thickness Lqw") #absorption in a quantum well slab, thickness Lqw
    #ax.axvline(sqrt(w0**2+wp**2)/2/pi)#line for sqrt(w0**2 + wp**2) (using Lqw not Leff)
    #ax.axvline(sqrt(w0**2-y**2+wp**2)/2/pi)#line for sqrt(w0**2 - y**2 + wp**2)
    ax.axvline(sqrt(w0**2+f12*wp**2)/2/pi)#line for sqrt(w0**2 + f12*wp**2) (using Lqw not Leff)
    ax.axvline(sqrt(w0**2-y**2+f12*wp**2)/2/pi)#line for sqrt(w0**2 - y**2 + f12*wp**2)
    
    ax.legend()
    pl.show()