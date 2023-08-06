#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# This file is part of pyFresnel.
# Copyright (c) 2012, Robert Steed
# Author: Robert Steed (rjsteed@talk21.com)
# License: GPL
# last modified 18.12.2012
import numpy as N
sin,arcsin,cos,arccos,exp=N.sin,N.arcsin,N.cos,N.arccos,N.exp
from Fresnel_equations import interface
c=299792458  #m/s - speed of light

class Plate():
    def __init__(self,n1,d,w,theta,n0=1.0,n2=1.0):
        self.n0=n0 #refractive index of initial medium
        self.n1=n1 #refractive index of plate
        self.n2=n2 #refractive index of exit medium
        self.d=d #thickness of plate (m)
        self.w=w #natural frequency (Hz)
        self.theta=theta+0j #angle of incidence (rad)
        self.i1=interface(n0,n1,theta) #first interface
        #self.i1b=interface(n1,n0,self.i1.internal_angle()) #first interface from inside
        self.i2=interface(n1,n2,self.i1.internal_angle()) #second interface
        
    def _phases(self,pol):
        k=self.n1*self.w/c
        phi=2*k*cos(self.i1.internal_angle())*self.d
        xi=phi/2.0
        #xi=phi/2.0 - k*cos(self.theta)*self.d/self.n1 # I believe that this is more accurate but does it matter? Not in most cases.
        expphi=exp(1j*phi)
        expxi=exp(1j*xi)
        return expphi,expxi
    
    def r_s(self):
        r01=self.i1.r_s()
        t01=self.i1.t_s()
        r12=self.i2.r_s()
        r10=-r01 #self.i1.r_s_b() #self.i1b.r_p()
        t10=self.i1.t_s_b() #self.i1b.t_s()
        expphi,expxi=self._phases('s')
        #
        r_s= r01 + (r12*t01*t10*expphi)/(1 - r10*r12*expphi)
        #r_s= (r01 + r12*expphi)/(1 + r01*r12*expphi)
        return r_s        
    
    def r_p(self):
        r01=self.i1.r_p()
        t01=self.i1.t_p()
        r12=self.i2.r_p()
        r10=-r01 #self.i1.r_p_b() #self.i1b.r_p()
        t10=self.i1.t_p_b() #self.i1b.t_p()
        expphi,expxi=self._phases('p')
        #
        r_p= r01 + (r12*t01*t10*expphi)/(1 - r10*r12*expphi)
        #r_p= (r01 + r12*expphi)/(1 + r01*r12*expphi)
        return r_p  
    
    def t_s(self):
        t01=self.i1.t_s()
        r12=self.i2.r_s()
        t12=self.i2.t_s()
        r10=-self.i1.r_s() #self.i1.r_s_b() #self.i1b.r_s()
        expphi,expxi=self._phases('s')
        #
        t_s= (t01*t12*expxi)/(1 - r10*r12*expphi)
        return t_s  
        
    def t_p(self):
        t01=self.i1.t_p()
        r12=self.i2.r_p()
        t12=self.i2.t_p()
        r10=-self.i1.r_p() #self.i1.r_p_b() #self.i1b.r_p()
        expphi,expxi=self._phases('p')
        #
        t_p= (t01*t12*expxi)/(1 - r10*r12*expphi)
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
        m=self.n2/self.n0
        p=cos(self.i2.internal_angle())/cos(self.theta)
        return (m*p*self._modsq(t_s)).real
    
    def T_p(self):
        t_p=self.t_p()
        m=self.n2/self.n0
        p=cos(self.i2.internal_angle())/cos(self.theta)
        return (m*p*self._modsq(t_p)).real
   

if __name__=="__main__":
    import matplotlib.pyplot as pl
    pi=N.pi
    ax=pl.subplot(111)
    f=N.arange(100e12,1500e12,5e10)
    w=2*pi*f
    
    slab=Plate(n1=3.0+0.05j,d=1e-6,w=w,theta=0.0,n0=1.0,n2=3.0+0j)  
    ax.plot(f,slab.T_s(),label='T_s')
    ax.plot(f,slab.T_p(),label='T_p')   
    
    slab=Plate(n1=3.0+0.05j,d=1e-6,w=w,theta=0.0,n0=1.0,n2=3.0+10j)  
    ax.plot(f,slab.T_s(),label='T_s n2=10+10j')
    ax.plot(f,slab.T_p(),label='T_p n2=10+10j') 
    
    ax.legend()
    pl.show()