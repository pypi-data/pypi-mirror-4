#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# This file is part of pyFresnel.
# Copyright (c) 2012, Robert Steed
# Author: Robert Steed (rjsteed@talk21.com)
# License: GPL
# last modified 18.12.2012
"""A simple Optical Transfer Matrix code (there are so many out there). It takes a description
of the layers and calculates the transmission and reflection. I will include a very special
anisotropic case where the dielectric is different along the perpendicular/ layer stack axis 
than to the in-plane directions; this is so I can describe quantum well intersubband absorptions.
If I have time, I will include code to calculate the intensity for each layer (for modelling
saturation of structures)."""

##Summary of maths


##Implementation
#Transfer matrix involves 2x2 matrices and multiplication but this needs to be 
#done for each frequency/wavelength.

#numpy method 1
#A = N.empty((numpts,),dtype=object) #this creates an array of objects that can be filled with anything, including matrices

#numpy method2
#A = N.zeros((numpts,2,2)) #creates a 3d array
#C = N.sum(np.transpose(A,(0,2,1)).reshape(100,2,2,1)*B.reshape(100,2,1,2),-3)#this can be used to matrix multiply 2 such arrays (very ugly isn't it)
#C = N.dot(A,B) #does this work? not quite. 
#use 
#N.diagonal(N.dot(A,B),axis1=0,axis2=2).swapawes(1,2).swapaxes(0,1)
#or
#N.rollaxis(N.diagonal(N.dot(A,B),axis1=0,axis2=2),2)
#or
#N.transpose(N.diagonal(N.dot(A,B),axis1=0,axis2=2),(2,0,1))
#but unecessary calculations are carried out by N.dot() so it is better to do
# N.sum(N.transpose(A,(0,2,1))[:,:,:,N.newaxis]*B[:,:,N.newaxis,:],axis=-3)

# see also einsum() and tensordot()

##Describing layers
#Can describe system as 
#
#f1 = filter([Layer(eps0,d0),
#            Layer(eps1,d1),
#            Layer(eps3,d2),
#            ...
#            ],w,pol,theta)
# but can use any python list operation required to make the process more efficient, i.e. f1*3 will repeat the structure 3 times.
# F1.append(Layer(epsn,dn)) will append a layer.


import numpy as N
c =299792458  #m/s - speed of light

class Layer():
    def __init__(self,eps,d):
        self.eps = eps # can be a function or array (if it has the same length as the spectral axis)
        self.d = d
        
    def n(self,w):
        try: #Is self.eps a function of w?
            n = N.sqrt(self.eps(w))
        except:
            #Is self.eps an array with the same length as w? 
            if hasattr(self.eps,'__len__'):
                if len(self.eps)!=len(w):
                    raise NameError("w and epsilon arrays are not compatible")
                else:
                    n = N.sqrt(self.eps)
            else: #Is self.eps a number (integer/float/complex)
                n = N.repeat(N.sqrt(self.eps),len(w))

        return n
        
    def __repr__(self):
        return "Layer"+"("+repr(self.eps)+", "+repr(self.d)+" )"

class Layer_Uniaxial():
    def __init__(self,epsxx,epszz,d):
        self.epsxx = epsxx # can be a function or array (if it has the same length as the spectral axis)
        self.epszz = epszz # can be a function or array (if it has the same length as the spectral axis)
        self.d = d
    
    def n(self,w):
        try: #Is self.eps a function of w?
            n = N.sqrt(self.epsxx(w))
        except:
            #Is self.eps an array with the same length as w? 
            if hasattr(self.epsxx,'__len__'):
                if len(self.epsxx)!=len(w):
                    raise NameError("w and epsilon arrays are not compatible")
                else:
                    n = N.sqrt(self.epsxx)
            else: #Is self.eps a number (integer/float/complex)
                n = N.repeat(N.sqrt(self.epsxx),len(w))

        return n

    def nzz(self,w):
        try: #Is self.eps a function of w?
            n = N.sqrt(self.epszz(w))
        except:
            #Is self.eps an array with the same length as w? 
            if hasattr(self.epszz,'__len__'):
                if len(self.epszz)!=len(w):
                    raise NameError("w and epsilon arrays are not compatible")
                else:
                    n = N.sqrt(self.epszz)
            else: #Is self.eps a number (integer/float/complex)
                n = N.repeat(N.sqrt(self.epszz),len(w))

        return n
        
    def __repr__(self):
        return "Layer"+"("+repr(self.epsxx)+", "+repr(self.epszz)+", "+repr(self.d)+" )"
        
class filter(list):
    def __init__(self,fltrlst,w=None,pol='TE',theta=0.0,*args,**kwargs):
        """Object to describe a stack of dielectric layers. fltrlist is a list of 
        Layer objects (any object that has a method n(w) for the refractive index and
        and a property d for the layer thickness will be suitable). w is the frequency (natural),
        pol is the polarisation and should be either 'TE' or 'TM'. theta is the angle 
        of incidence (degrees)."""
        list.__init__(self,fltrlst,*args,**kwargs)
        if w == None:
            w=N.array([1.0])
        if type(w) == type(float()) or type(w) == type(int()):
            w=N.array([w])
        self.w=w
        self.pol=pol
        self.theta=theta
        self.n0sinth2=(fltrlst[0].n(w) * N.sin(theta*N.pi/180.0))**2
        #decide whether axis is frequency or angle of incidence
        if hasattr(theta,'__iter__'):
            assert len(w)==1, "Can not vary both frequency and angle at the same time"
            self.axis=theta
        else:
            self.axis=w
        
    def __repr__(self):
        return repr(self[:]) + ", w= "+repr(self.w)+", pol= "+repr(self.pol)+", theta= "+repr(self.theta)
        
    def __str__(self):
        globals = "w : %s\npol : %s\ntheta : %s" %(repr(self.w),repr(self.pol),repr(self.theta))
        stack = "[\n"+",\n".join([repr(l) for l in self ])+"\n]"
        return globals + '\n' +stack
        
    def _lambda(self,layer_pair):
        """Calculates a variable needed to create the interface matrices"""
        # Special code to account for a special case of anisotropic medium
        if hasattr(layer_pair[1],'nzz') and self.pol=='TM':
            n1 = layer_pair[1].nzz
        else:
            n1 = layer_pair[1].n
        
        if hasattr(layer_pair[0],'nzz') and self.pol=='TM':
            n0 = layer_pair[0].nzz
        else:
            n0 = layer_pair[0].n
        
        w = self.w
        cos_ratio = N.sqrt(1+0j - self.n0sinth2 / n1(w)**2 ) # uses 1+0j to cast argument to complex so that we can describe totoal internal reflection.
        cos_ratio = cos_ratio/N.sqrt(1+0j - self.n0sinth2 / n0(w)**2 ) 
        n_ratio = layer_pair[1].n(w) / layer_pair[0].n(w)
        
        if self.pol=='TE':
            lmda = cos_ratio * n_ratio
        elif self.pol=='TM':
            lmda = cos_ratio / n_ratio
        else: 
            raise NameError("pol should be 'TE' or 'TM'")
        return lmda
    
    def _phase(self,layer):
        """Phase change for a layer. Returns a 1d array of phase vs frequency."""
        #special code to account for a special case of anisotropic medium
        if hasattr(layer,'nzz') and self.pol=='TM':
            n1 = layer.nzz
        else:
            n1 = layer.n
            
        w = self.w
        k = layer.n(w) * w / c
        costh = N.sqrt(1+0j - self.n0sinth2 / n1(w)**2 ) 
        return k * layer.d * costh
        
    def layer_array(self,layer):
        """array of 'matrices' describing the phase change across the layer wrt frequency"""
        phase=self._phase(layer)
        nph=N.exp(-1j*phase)
        pph=N.exp(1j*phase)
        matrix = 0.5*N.column_stack((nph,N.zeros_like(w),N.zeros_like(w),pph))
        matrix.shape = (len(self.axis),2,2)
        return matrix
        
    def interface_array(self,layer_pair):
        """array of 'matrices' describing the interface between 2 layers wrt frequency"""
        lmda=self._lambda(layer_pair)
        matrix = 0.5*N.column_stack(((1+lmda),(1-lmda),(1-lmda),(1+lmda)))
        matrix.shape = (len(self.axis),2,2)
        return matrix
        
    def layer_array2(self,layer_pair):
        """array of 'matrices' describing the interface and also phase change for the layer wrt frequency"""
        phase=self._phase(layer_pair[1])
        nph=N.exp(-1j*phase)
        pph=N.exp(1j*phase)
        lmda=self._lambda(layer_pair)
        matrix = 0.5*N.column_stack(((1+lmda)*nph,(1-lmda)*pph,(1-lmda)*nph,(1+lmda)*pph))
        matrix.shape = (len(self.axis),2,2)
        return matrix
        
    def calculate_M(self):
        """Calculates the system matrix"""
        I = N.array(((1,0),(0,1)))
        tmp = N.array( (I,)*len(self.w) ) # running variable to hold the calculation results. Starts as an array of identity 'matrices'
        for layer_pair in zip(self,self[1:])[:-1]:
            nl = self.layer_array2(layer_pair)
            tmp = N.sum(N.transpose(tmp,(0,2,1))[:,:,:,N.newaxis]*nl[:,:,N.newaxis,:],axis=-3)
        #final interface before substrate
        layer_pair=(self[-2],self[-1])
        tmp = N.sum(N.transpose(tmp,(0,2,1))[:,:,:,N.newaxis]*self.interface_array(layer_pair)[:,:,N.newaxis,:],axis=-3)
        return tmp
        
    def calculate_r_t(self):
        """Calculates the reflection and transmission coefficients"""
        axis = self.axis
        w = self.w
        M = self.calculate_M()
        t = 1.0/M[:,0,0]
        if self.pol=='TM': #extra polarisation sensitive term for t 
            t*=self[0].n(w)/self[-1].n(w)
        r = M[:,1,0]/M[:,0,0]
        return (axis,r,t)
    
    def calculate_R_T(self):
        """Calculates the Reflectivity and Transmission of the stack"""
        axis = self.axis
        M = self.calculate_M()
        t = 1.0/M[:,0,0]
        T = t*t.conjugate()*self._lambda((self[0],self[-1]))
        r = M[:,1,0]/M[:,0,0]
        R = r*r.conjugate()
        return (axis,R,T)

if __name__ == "__main__":
    pi=N.pi
    f=N.linspace(1.0e10,10e12,200)
    f1 = filter([Layer(1.0,None),
            Layer(3.50,8e-6),
            Layer(12.25,None)],
            w=2*pi*f)
    print f1
    #print repr(f1)
    #print len(f1)
    #print f1.calculate_M()[0]
    #print f1._lambda((f1[0],f1[-1]))
    #print f1.calculate_r_t()[0]
    w,R,T=f1.calculate_R_T()
    import matplotlib.pyplot as P
    
    ax1 = P.subplot(111)
    ax1.plot(f,R,label="reflection")
    ax1.plot(f,T,label="Transmission")
    
    ax1.set_title("Antireflection coating for GaAS or Silicon")
    ax1.legend()
    P.show()
