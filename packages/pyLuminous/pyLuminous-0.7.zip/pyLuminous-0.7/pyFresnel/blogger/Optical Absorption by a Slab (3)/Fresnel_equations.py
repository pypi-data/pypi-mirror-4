#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# This file is part of pyFresnel.
# Copyright (c) 2012, Robert Steed
# Author: Robert Steed (rjsteed@talk21.com)
# License: GPL
# last modified 18.12.2012
import numpy as N
sin,arcsin,cos,arccos=N.sin,N.arcsin,N.cos,N.arccos
#from types import ComplexType


class interface():
    
    convention=-1 #The commonest convention issue is in the chosen sign of r_p. -1 agrees with Hecht, many others will use +1
    
    def __init__(self,n1=1.0,n2=1.0,theta=0.0):
        self.n1=n1
        self.n2=n2
        self.theta=theta+0j #I want to be able to use complex angles.
                
    def internal_angle(self):
        return arcsin(self.n1/self.n2*sin(self.theta))
    
    def _core(self,pol):
        m=cos(self.internal_angle())/cos(self.theta)
        p=self.n2/self.n1
        return m,p
    
    def _modsq(self,a):
        if hasattr(a,"conjugate"):
            return a*a.conjugate()
        else:
            return a*a
        
    def r_s(self):
        m,p=self._core('s')
        return (1.0 - p*m)/(1.0 + p*m)
        
    def r_p(self):
        m,p=self._core('p')
        return self.convention*(m - p)/(m + p)
        
    def t_s(self):
        m,p=self._core('s')
        return 2.0/(1.0 + m*p)
        
    def t_p(self):
        m,p=self._core('p')
        return 2.0/(m + p)
        
    def R_s(self):
        r_s=self.r_s()
        return self._modsq(r_s).real
        
    def R_p(self):
        r_p=self.r_p()
        return self._modsq(r_p).real
        
    def T_s(self):
        t_s=self.t_s()
        m,p=self._core('s')
        return (m*p*self._modsq(t_s)).real
        
    def T_p(self):
        t_p=self.t_p()
        m,p=self._core('p')
        return (m*p*self._modsq(t_p)).real
        
    #coefficients for waves coming from other side of interface
    
    def r_s_b(self):
        m,p=self._core('s')
        return -(1.0 - p*m)/(1.0 + p*m)
        
    def r_p_b(self):
        m,p=self._core('p')
        return -self.convention*(m - p)/(m + p)
        
    def t_s_b(self):
        m,p=self._core('s')
        return 2.0*m*p/(1.0 + m*p)
        
    def t_p_b(self):
        m,p=self._core('p')
        return 2.0*m*p/(m + p)
    
    #R_s_b=R_s
    #R_p_b=R_p
    #T_s_b=T_s
    #T_p_b=T_ss
    
    def R_s_b(self):
        r_s=self.r_s_b('s')
        return self._modsq(r_s).real
        
    def R_p_b(self):
        r_p=self.r_p_b('p')
        return self._modsq(r_p).real
        
    def T_s_b(self):
        t_s=self.t_s_b()
        m,p=self._core('s')
        return (1.0/(m*p)*self._modsq(t_s)).real
        
    def T_p_b(self):
        t_p=self.t_p_b()
        m,p=self._core('p')
        return (1.0/(m*p)*self._modsq(t_p)).real
    
    
if __name__=="__main__":
    import pylab as pl
    pi=pl.pi
    
    f1=pl.figure(1)
    ax1=f1.add_subplot(111)
    f2=pl.figure(2)
    ax2=f2.add_subplot(111)
    
    theta=pl.arange(0.0,90.0,0.2)
    theta2=theta*pi/180.0
    I=interface(n1=1.0,n2=1.5,theta=theta2)
    
    ax1.plot(theta,I.r_s(),label="r_s")
    ax1.plot(theta,I.r_p(),label="r_p")
    ax1.plot(theta,I.t_s(),label="t_s")
    ax1.plot(theta,I.t_p(),label="t_p")
    ax1.legend()
    
    ax2.plot(theta,I.R_s(),label="R_s")
    ax2.plot(theta,I.R_p(),label="R_p")
    ax2.plot(theta,I.T_s(),label="T_s")
    ax2.plot(theta,I.T_p(),label="T_p")
    ax2.legend()
    
    pl.show()