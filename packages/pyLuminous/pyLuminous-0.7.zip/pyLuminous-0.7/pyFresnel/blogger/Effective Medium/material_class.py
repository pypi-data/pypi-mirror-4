
#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# This file is part of pyFresnel.
# Copyright (c) 2012, Robert Steed
# Author: Robert Steed (rjsteed@talk21.com)
# License: GPL
# last modified 18.12.2012

#sort out api for frequencies
#sort out real vs natural frequencies.

import numpy as N
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
        """
        n=self.n()
        if hasattr(n,"conjugate"):
            real=n.real**2-n.imag**2
            imag=2*n.real*n.imag
            eps=real+1.0j*imag
        else:
            eps=n**2
        return eps
        """

    def n(self):
        return sqrt(self.epsilon())
        """
        eps=self.epsilon()
        if hasattr(eps,"conjugate"):
            term2=sqrt(eps*eps.conjugate())
            real=sqrt((eps.real+term2)/2.0)
            imag=sqrt((-eps.real+term2)/2.0)
            imag*=(eps.imag>0)*2-1
            n=real+1.0j*imag
        else:
            n=sqrt(eps)
        return n
        """
        
    def __len__(self):
        pass
        
    def __add__(self,other): # this might not work once we start using the Claussius-Claussis relation!
        """Add two derived instances of classes derived from material"""
        def new_epsilon(self2):
            return self.epsilon()+other.epsilon()
        newmat=material()
        newmat.epsilon=new_epsilon.__get__(newmat,material) # binds function to instance
        return newmat

######################################

class material_eps(material):
    """initialise using material_eps(epsilon). epsilon can be a (complex) number or array"""
    def __init__(self,eps):
        material.__init__(self)
        self.eps=eps
    
    def epsilon(self):
        return self.eps
    
class material_nk(material):
    """initialise using material_nk(nk). nk can be a (complex) number or array"""
    def __init__(self,nk):
        material.__init__(self)
        self.nk=nk
        
    def n(self):
        return self.nk


######################################

class Lorentz_model(material):
    """Simple model of an absorbing oscillator / transition.
    Frequencies - whether we use real or natural frequency doesn't matter as long as we are consistant! 
    Remember that there is a difference of 2pi between the two: w=2*pi*f
    Note that normally the equations for the plasma frequency will give a natural frequency but that otherwise
    will be interested in real frequencies."""
    def __init__(self,w,w0,y,wp,f,eps_b):
        #So if we use real frequencies, the plasma frequency must be real too (and the normal equations give a natural value).
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
    
class Drude_model(material):
    """Simple model of a plasma"""
    def __init__(self,w,y,wp,f,eps_b):
        self.w=w
        self.y=y
        self.wp=wp
        self.f=f
        self.eps_b=eps_b
    
    def epsilon(self):
        w,y,wp,f,eps_b=self.w,self.y,self.wp,self.f,self.eps_b
        eps=eps_b*(1-wp**2*f/(w**2+2j*y*w))
        return eps
    
    @staticmethod    
    def wp(N,meff,eps_b):
        """N (m**-3) charge density
        meff (fraction of m_e) effective mass
        eps_b (unitless) background dielectric"""
        return sqrt(N*q**2/(meff*m_e*eps0*eps_b))
               
"""        
class metal(material):
    ""Simplified refractive index model of a metal at low frequencies.
    sigma0 (/Ohm/m) dc conductivity
    eps_b (unitless) background dielectric""
    def __init__(self,sigma0,eps_b,simple_n=True):
        self.sigma0=sigma0
        self.eps_b=eps_b
        
        if simple_n==True: #over-riding more exact calculation of refractive index
            def n(self):
                sigma0,eps_b=self.sigma0,self.eps_b
                p=sqrt(sigma0/(2.0*eps0*w))
                return (1+1j)*p
                
            self.n=n.__get__(self,metal) # binds function to instance
    
    def epsilon(self):
        sigma0,eps_b=self.sigma0,self.eps_b
        eps=eps_b+1j*sigma0/eps0/w
        return eps
"""

class metal(material):
    """Simplified refractive index model of a metal at low frequencies.
    sigma0 (/Ohm/m) dc conductivity
    eps_b (unitless) background dielectric"""
    def __init__(self,w,sigma0,eps_b,simple_n=True):
        self.w=w
        self.sigma0=sigma0
        self.eps_b=eps_b        
        if simple_n==False: #to use more exact calculation of refractive index
            self.n=super(metal2,self).n # reverting to function from base class
            
    def epsilon(self):
        w,sigma0,eps_b=self.w,self.sigma0,self.eps_b
        eps=eps_b+1j*sigma0/eps0/w
        return eps
    
    def n(self):
        w,sigma0,eps_b=self.w,self.sigma0,self.eps_b
        p=sqrt(sigma0/(2.0*eps0*w))
        return (1+1j)*p
    
    @staticmethod    
    def wp(N,meff,eps_b):
        """N (m**-3) charge density
        meff (fraction of m_e) effective mass
        eps_b (unitless) background dielectric"""
        return sqrt(N*q**2/(meff*m_e*eps0*eps_b))

    @staticmethod    
    def sigma0(N,meff,y):
        """N (m**-3) charge density
        meff (fraction of m_e) effective mass
        eps_b (unitless) background dielectric"""
        return N*q**2/(meff*m_e*2*y)
        
    @staticmethod    
    def sigma0_b(wp,y,eps_b):
        """N (m**-3) charge density
        meff (fraction of m_e) effective mass
        eps_b (unitless) background dielectric"""
        return wp**2*eps0*eps_b/(2*y) 


class metal2(material):
    """Simplified refractive index model of a metal at low frequencies.
    sigma0 (/Ohm/m) dc conductivity
    eps_b (unitless) background dielectric
    Actually, this is the Drude model reformulated."""
    def __init__(self,w,sigma0,y,eps_b,simple_n=True):
        self.w=w
        self.sigma0=sigma0
        self.eps_b=eps_b
        self.y=y
            
    def epsilon(self):
        w,sigma0,y,eps_b=self.w,self.sigma0,self.y,self.eps_b
        sigma=sigma0*2*y/(2*y-1j*w)
        eps=eps_b+1j*sigma/eps0/w
        return eps
    
    @staticmethod    
    def wp(N,meff,eps_b):
        """N (m**-3) charge density
        meff (fraction of m_e) effective mass
        eps_b (unitless) background dielectric"""
        return sqrt(N*q**2/(meff*m_e*eps0*eps_b))

    @staticmethod    
    def sigma0(N,meff,y):
        """N (m**-3) charge density
        meff (fraction of m_e) effective mass
        eps_b (unitless) background dielectric"""
        return N*q**2/(meff*m_e*2*y)
        
    @staticmethod    
    def sigma0_b(wp,y,eps_b):
        """N (m**-3) charge density
        meff (fraction of m_e) effective mass
        eps_b (unitless) background dielectric"""
        return wp**2*eps0*eps_b/(2*y)

######################################

class gold(material): #taken from paper by Etchegoin 2006
    def __init__(self,w):
        self.w=w
    
    def epsilon(self):
        w=self.w
        epsinf=1.53
        wp=12.9907004642E15 #Hz (natural)
        Gammap=110.803033371e12 #Hz (natural)
        C1=3.78340272066E15 #Hz (natural)
        w1=4.02489651134E15 #Hz (natural)
        Gamma1=0.818978942308E15 #Hz (natural)
        C2=7.73947471764E15 #Hz (natural)
        w2=5.69079023356E15 #Hz (natural)
        Gamma2=2.00388464607E15 #Hz (natural)
        sr2=sqrt(2)
        G1=C1*( (1-1j)/sr2/(w1 - w - 1j*Gamma1) + (1+1j)/sr2/(w1 + w + 1j*Gamma1) )
        G2=C2*( (1-1j)/sr2/(w2 - w - 1j*Gamma2) + (1+1j)/sr2/(w2 + w + 1j*Gamma2) )
        eps= epsinf - wp**2/(w**2+1j*w*Gammap) + G1 + G2
        
        return eps        
    
class gold_test(material): #an experiment to see difference of above model from plasma + 2 Lorentz oscillators
    def __init__(self,w):
        self.w=w
    
    def epsilon(self):
        w=self.w
        epsinf=1.53
        wp=12.9907004642E15 #Hz (natural)
        Gammap=110.803033371e12 #Hz (natural)
        C1=3.78340272066E15 #Hz (natural)
        w1=4.02489651134E15 #Hz (natural)
        Gamma1=0.818978942308E15 #Hz (natural)
        C2=7.73947471764E15 #Hz (natural)
        w2=5.69079023356E15 #Hz (natural)
        Gamma2=2.00388464607E15 #Hz (natural)
        sr2=sqrt(2)
        G1=C1*( 1.0/(w1 - w - 1j*Gamma1) + 1.0/(w1 + w + 1j*Gamma1) )
        G2=C2*( 1.0/(w2 - w - 1j*Gamma2) + 1.0/(w2 + w + 1j*Gamma2) )
        eps= epsinf - wp**2/(w**2+1j*w*Gammap) + G1 + G2
        
        return eps
        


class Yanko_gold(material):
    """Gold used for Yanko's Smatrix program. For THz frequencies"""
    def __init__(self,w):
        self.w=w #natural frequency
        
    def epsilon(self):
        w=self.w*1e-12
        eps= 1.0 - 0.6e8/(w * (w + 100.0j))
        return  eps    

######################################

class GaAs(material): #GaAs dielectric including phonon band.
    pass
    
class Yanko_GaAs(material): 
    """GaAs dielectric including phonon band as used in Yanko's Smatrix program.
    Works for THz frequencies"""
    def __init__(self,w,n=0.0):
        """n = doping (1E18 cm-3)"""
        self.w=w #natural frequency
        self.doping=n
        
    def epsilon(self):
        w=self.w*1e-12
        eps= 10.4  + 5161.4 / (2620.0 - w**2 -0.2j*w)
        
        #including effect of doping
        n=self.doping
        if n!=0.0:
            if n<1.0: T=10.0/(1.0 - 2.0*N.log10(n))
            else: T=10.0
            eps-= 47436.84*n / (w*(w+1j*T))
        return  eps   

class Yanko_GaAsC(material): 
    """GaAs dielectric including phonon band as used in Yanko's Smatrix program.
    Works for THz frequencies"""
    def __init__(self,w,n=0.0):
        """n = doping (1E18 cm-3)"""
        self.w=w #natural frequency
        self.doping=n
        
    def epsilon(self):
        w=self.w*1e-12
        eps= 10.88  + 5029.042 / (2552.81 - w**2 -0.377j*w)
        
        #including effect of doping
        n=self.doping
        if n!=0.0:
            if n<1.0: T=10.0/(1.0 - 2.0*N.log10(n))
            else: T=10.0
            eps-= 47436.84*n / (w*(w+1j*T))
        return  eps 

class AlGaAs(material): #AlGaAs dielectric including phonon band.
    pass
    
class QW_ISBT_unconventional(material): #includes wp, f12, damping, no depolarization shift, background dielectric
    """epsilon=eps_well+wp**2*f12/(w0**2-w**2-2j*y*w))
    wp**2=N*q**2/(meff*m_e*eps0*eps_well)
    w0 - frequency (?)
    y - scattering rate (?)
    wp - plasma frequency (?)
    eps_well - background dielectric constant (unitless)
    This class doesn't include the background dielectric constant within the 
    plasma frequency which allows more exactly for frequency dependence in the
    background dielectric constant but it's better normally to follow convention
    in order to avoid confusion.
    """
    def __init__(self,w,w0,y,f12,wp,eps_well):
        self.w=w
        self.w0=w0
        self.y=y
        self.f12=f12
        self.wp=wp
        self.eps_well=eps_well
        
    def epsilon(self):
        w=self.w; w0=self.w0; y=self.y; f12=self.f12; wp=self.wp; eps_well=self.eps_well
        eps=eps_well+wp**2*f12/(w0**2-w**2-2j*y*w)
        return eps
    
    @staticmethod
    def wp(N,meff=0.067):
        """N  (cm**-3) 3D charge density
        eps_well (unitless) the background dielectric constant around the frequency of the transition
        meff (unitless - fraction of electron mass) effective mass of the electrons"""
        N*=100**3 #converts density to m**-3
        return sqrt(N*q**2/(meff*m_e*eps0)) #doesn't include eps_well like other definitions
        
class QW_ISBT(material): #includes wp, f12, damping, no depolarization shift, background dielectric
    """epsilon=eps_well*(1.0+wp**2*f12/(w0**2-w**2-2j*y*w))
    wp**2=N*q**2/(meff*m_e*eps0*eps_well)
    w0 - frequency (?)
    y - scattering rate (?)
    wp - plasma frequency (?)
    eps_well - background dielectric constant (unitless)
    """
    def __init__(self,w,w0,y,f12,wp,eps_well):
        self.w =w; self.w0=w0; self.y=y; 
        self.f12=f12; self.wp=wp; self.eps_well=eps_well
        
    def epsilon(self):
        w=self.w; w0=self.w0; y=self.y; f12=self.f12; wp=self.wp; eps_well=self.eps_well
        eps=eps_well*(1.0+wp**2*f12/(w0**2-w**2-2j*y*w))
        return eps
    
    @staticmethod
    def wp(N,eps_well,meff=0.067):
        """N  (cm**-3) 3D charge density
        eps_well (unitless) the background dielectric constant around the frequency of the transition
        meff (unitless - fraction of electron mass) effective mass of the electrons"""
        N*=100**3 #converts density to m**-3
        return sqrt(N*q**2/(meff*m_e*eps0*eps_well))
        
class QW_ISBT_gain(material): #includes wp, f12, damping, no depolarization shift, background dielectric
    """epsilon=eps_well*(1.0+wp**2*f12/(w0**2-w**2-2j*y*w))
    wp**2=N*q**2/(meff*m_e*eps0*eps_well)
    w0 - frequency (?)
    y - scattering rate (?)
    wp - plasma frequency (?)
    eps_well - background dielectric constant (unitless)
    """
    def __init__(self,w,w0,y,f12,wp,eps_well):
        self.w =w; self.w0=w0; self.y=y; 
        self.f12=f12; self.wp=wp; self.eps_well=eps_well
        
    def epsilon(self):
        w=self.w; w0=self.w0; y=self.y; f12=self.f12; wp=self.wp; eps_well=self.eps_well
        eps=eps_well*(1.0+wp**2*f12/(w0**2-w**2-2j*y*w))
        return N.conjugate(eps)
    
    @staticmethod
    def wp(N,eps_well,meff=0.067):
        """N  (cm**-3) 3D charge density
        eps_well (unitless) the background dielectric constant around the frequency of the transition
        meff (unitless - fraction of electron mass) effective mass of the electrons"""
        N*=100**3 #converts density to m**-3
        return sqrt(N*q**2/(meff*m_e*eps0*eps_well))
        
        
if __name__=="__main__":
    
    import pylab as pl
    pl.figure(1)
    ax1=pl.subplot(311)
    ax2=pl.subplot(312, sharex=ax1)
    ax3=pl.subplot(313,sharex=ax1)
    w=pl.arange(0,5e12,5e9)
    L=Lorentz_model(w=w,w0=1e12,y=5e10,wp=8e11,f=0.96,eps_b=1.0)
    ax1.plot(w,L.epsilon().real,label="epsilon real")
    ax1.plot(w,L.epsilon().imag,label="epilon imaginary")
    ax2.plot(w,L.n().real,label="refractive index")
    ax2.plot(w,L.n().imag,label="kappa")
    ax3.plot(w,2*w*L.n().imag/c,label="absorption coefficient")
    for ax in ax1,ax2,ax3:
        ax.axvline(L.w0) #w0
        ax.axvline(sqrt(L.w0**2-L.y**2)) #damping shifted peak
        #We don't see a depolarisation shift in this geometry so no point confusing you...yet.
        #ax.axvline(sqrt(L.w0**2+L.wp**2*L.f)) #depolarisation shifted peak #2
        #ax.axvline(sqrt(L.w0**2+L.wp**2)) #depolarisation shifted peak
        #ax.axvline(sqrt(L.w0**2-L.y**2+L.wp**2*L.f)) #depolarisation + damping shifted peak #2 
        #ax.axvline(sqrt(L.w0**2-L.y**2+L.wp**2)) #depolarisation + dampiing shifted peak
    ax1.legend()
    ax2.legend()
    ax3.legend()
    ax1.set_title("Various properties of an example Lorentzian Oscillator")
    ax3.set_xlabel("Frequency (real) (Hz)")
    ax3.text(1.4e12,4000,"It is interesting that the absorption coefficient plotted here is \n \
nothing like the profile, we would see if we modelled the \n \
absorption of a slab of this material"  )
    #
    pl.figure(2)
    ax1=pl.subplot(311)
    ax2=pl.subplot(312, sharex=ax1)
    ax3=pl.subplot(313,sharex=ax1)
    w=pl.arange(0,5e12,5e9)
    D=Drude_model(w=w,y=5e10,wp=8e11,f=0.96,eps_b=1.0)
    ax1.plot(w,D.epsilon().real,label="epsilon real")
    ax1.plot(w,D.epsilon().imag,label="epilon imaginary")
    ax2.plot(w,D.n().real,label="refractive index")
    ax2.plot(w,D.n().imag,label="kappa")
    ax3.plot(w,2*w*D.n().imag/c,label="absorption")
    for ax in ax1,ax2,ax3:
        ax.axvline(D.wp) #w0
    ax1.legend()
    ax2.legend()
    ax3.legend()
    ax1.set_title("Various properties of an example Drude model")
    ax3.set_xlabel("Frequency (real) (Hz)")
    ax3.text(1.4e12,2000,"It is interesting that the absorption coefficient plotted here is \n \
nothing like the profile, we would see if we modelled the \n \
absorption of a slab of this material"  )    
    #
    pl.figure(3)
    ax1=pl.subplot(311)
    ax2=pl.subplot(312, sharex=ax1)
    ax3=pl.subplot(313,sharex=ax1)
    w=pl.arange(5e9,5e12,5e9)
    M=metal(w,sigma0=45.2e6,eps_b=1.0) #gold
    ax1.plot(w,M.epsilon().real,label="epsilon real")
    ax1.plot(w,M.epsilon().imag,label="epilon imaginary")
    ax2.plot(w,M.n().real,label="refractive index")
    ax2.plot(w,M.n().imag,label="kappa")
    ax3.plot(w,2*w*M.n().imag/c,label="absorption")
    ax1.legend()
    ax2.legend()
    ax3.legend()
    ax1.set_title("Various properties of an example of a metallic material")
    ax3.set_xlabel("Frequency (real) (Hz)")
    ax3.text(1.4e12,15e6,"It is interesting that the absorption coefficient plotted here is \n \
nothing like the profile, we would see if we modelled the \n \
absorption of a slab of this material"  )  
    # Gold at optical frequencies
    pl.figure(4)
    ax1=pl.subplot(211)
    ax2=pl.subplot(212, sharex=ax1)
    f=pl.arange(300e12,1500e12,5e10)
    w=2*pi*f
    G=gold(w) #
    G2=gold_test(w)
    for g in (G,G2):#,(G2):
        ax1.plot(c/f*1e9,g.epsilon().real,label="epsilon real")
        ax1.plot(c/f*1e9,g.epsilon().imag,label="epilon imaginary")
        ax2.plot(c/f*1e9,g.n().real,label="refractive index")
        ax2.plot(c/f*1e9,g.n().imag,label="kappa")
    ax1.legend()
    ax2.legend()
    ax1.set_title("Gold at optical frequencies")
    ax2.set_xlabel("Wavelength (nm)")
    
    #GaAs refractive index
    pl.figure(5)
    ax1=pl.subplot(111)
    f=pl.arange(300e9,20e12,100e9)
    w=2*pi*f
    GaAs=Yanko_GaAs(w)
    ax1.plot(f,GaAs.n().real,label="real part")
    ax1.plot(f,GaAs.n().imag,label="imag part")
    ax1.legend()
    ax1.set_title("Refractive index of GaAs for THz frequencies")
    ax1.set_xlabel("Frequency (real) (Hz)")
    ax1.text(9e12,10,"LO phonon interaction (polariton)")
        
        
    pl.show()   
