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


class Interface():
    
    convention=-1 #The commonest convention issue is in the chosen sign of r_p. -1 agrees with Hecht, many others will use +1
    
    def __init__(self,eps1xx=1.0,eps1zz=1.0,eps2xx=1.0,eps2zz=1.0,kx=0.0):
        self.eps1xx=eps1xx
        self.eps1zz=eps1zz
        self.eps2xx=eps2xx
        self.eps2zz=eps2zz
        
        self.kx=kx+0j #I want to be able to use complex k_vectors.
                    
    def _core(self,pol):
        """pol is 'p' or 's'"""
        eps1xx=self.eps1xx; n1xx=sqrt(eps1xx)
        eps1zz=self.eps1zz; n1zz=sqrt(eps1zz)
        eps2xx=self.eps2xx; n2xx=sqrt(eps2xx)
        eps2zz=self.eps2zz; n2zz=sqrt(eps2zz)
        #
        kx=self.kx
        #
        K=w/c
        if pol=='p':
            ?
            Lambda = k2z*eps1xx/(k1z*eps2xx)
        elif pol=='s':
            ?
            Lambda = k2z/k1z
        return Lambda
        
    def k1z(self):
        pass
        
    def k2z(self):
        pass
    
    def _modsq(self,a):
        if hasattr(a,"conjugate"):
            return a*a.conjugate()
        else:
            return a*a
        
    def r_s(self):
        Lambda=self._core('s')
        return (1.0- Lambda)/(1.0 + Lambda)
        
    def r_p(self):
        Lambda=self._core('p')
        return self.convention*(1.0- Lambda)/(1.0 + Lambda)
        
    def t_s(self):
        Lambda=self._core('s')
        return 2.0/(1.0 + Lambda)
        
    def t_p(self):
        Lambda=self._core('p')
        return 2.0/(1.0 + Lambda)*sqrt(self.eps1xx/self.eps2xx)
        
    def R_s(self):
        r_s=self.r_s()
        return self._modsq(r_s)
        
    def R_p(self):
        r_p=self.r_p()
        return self._modsq(r_p)
        
    def T_s(self):
        t_s=self.t_s()
        Lambda=self._core()
        return Lambda*self._modsq(t_s)
        
    def T_p(self):
        Lambda=self._core()
        return 4*Lambda/(1+Lambda)**2 #safer to recalculate than depend on convention chosen for t_p
            
            
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