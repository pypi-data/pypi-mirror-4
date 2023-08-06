"""Testing the isotropic part of the transfer matrix class using the metallic
tests from Freesnell. See the Freesnell website for details."""

import pyFresnelInit
import pyFresnel.transfer_matrix as TM
from metals_nk import Al,Au
Layer=TM.Layer
import numpy as N
import matplotlib.pyplot as P
pi=N.pi
c=299792458  #m/s - speed of light

## Protected Al
#From Freesnell, a reproduction of http://www.kruschwitz.com/HR%27s.htm
lamda = N.linspace(.3e-6,.9e-6,200) # (m) wavelength
w = 2*pi*c/lamda # (Hz) frequency (natural)

#refractive indices.
protectedAl = TM.Filter(
            [Layer(1.0,None),
            Layer(1.45, 1.75/4*.6e-6/1.45),
            Layer(Al,None)],
            w=w,
            pol='TM',
            theta=0.0)

protectedAl2 = TM.Filter(
            [Layer(1.0,None),
            Layer(2.0, 1.65/4*.6e-6/2.0),
            Layer(Al,None)],
            w=w,
            pol='TM',
            theta=0.0)
            
uncoatedAl =  TM.Filter(
            [Layer(1.0,None),
            Layer(Al,None)],
            w=w,
            pol='TM',
            theta=0.0)

ax1 = P.subplot(111)
ax1.set_title("Protected Aluminum Mirror @0deg incidence")

w,R,T=protectedAl.calculate_R_T()
ax1.plot(lamda*1e9,R,label="Protected Al (coating n=1.45)")

w,R,T=protectedAl2.calculate_R_T()
ax1.plot(lamda*1e9,R,label="Protected Al (coating n=2.0)")

w,R,T=uncoatedAl.calculate_R_T()
ax1.plot(lamda*1e9,R,label="Al (uncoated)")

ax1.set_ylim([0.7,0.95])
ax1.set_xlabel("wavelength (nm)")
ax1.set_ylabel("Reflection")
ax1.legend(loc=8)

P.figure()

ax1 = P.subplot(111)
ax1.set_title("Protected Aluminum Mirror @45 deg (unpolarised)")

w,Rp,Tp=protectedAl.calculate_R_T(theta=pi/4.,pol='TM')
w,Rs,Ts=protectedAl.calculate_R_T(theta=pi/4.,pol='TE')
ax1.plot(lamda*1e9,0.5*(Rp+Rs),label="Protected Al (coating n=1.45)")

w,Rp,Tp=uncoatedAl.calculate_R_T(theta=pi/4.,pol='TM')
w,Rs,Ts=uncoatedAl.calculate_R_T(theta=pi/4.,pol='TE')
ax1.plot(lamda*1e9,0.5*(Rp+Rs),label="Al (uncoated)")
ax1.legend(loc=8)
P.show()

##### More Coatings for Al
#Reproduction of Jaffer's reproduction of http://www.kruschwitz.com/HR%27s.htm#Enhanced Metal
#.. by increasing the number of periods, the
#reflectivity increases, but the high reflectivity region narrows.
lamda = N.linspace(300e-9,900e-9,200) # (m) wavelength
w = 2*pi*c/lamda # (Hz) frequency (natural)

H = 2.40 #refractive indices
L = 1.46 #

nom = 550e-9

advAlcoating = TM.Filter(
            [Layer(1.0,None),
            Layer(H, 0.25*nom/H),
            Layer(L, 0.25*nom/L),
            Layer(Al,None)],
            w=w,
            pol='TM',
            theta=0.0)

advAlcoating2 = TM.Filter(
            [Layer(1.0,None),
            Layer(H, 0.25*nom/H),
            Layer(L, 0.25*nom/L),
            Layer(H, 0.25*nom/H),
            Layer(L, 0.25*nom/L),
            Layer(Al,None)],
            w=w,
            pol='TM',
            theta=0.0)
            
advAlcoating3 = TM.Filter(
            [Layer(1.0,None),
            Layer(H, 0.25*nom/H),
            Layer(L, 0.25*nom/L),
            Layer(H, 0.25*nom/H),
            Layer(L, 0.25*nom/L),
            Layer(H, 0.25*nom/H),
            Layer(L, 0.25*nom/L),
            Layer(Al,None)],
            w=w,
            pol='TM',
            theta=0.0)
            
uncoatedAl =  TM.Filter(
            [Layer(1.0,None),
            Layer(Al,None)],
            w=w,
            pol='TM',
            theta=0.0)

ax1 = P.subplot(111)
ax1.set_title("Enhanced Aluminum Mirror")

w,R,T=advAlcoating.calculate_R_T()
ax1.plot(lamda*1e9,R,label="Coated Al: 1 repeat")

w,R,T=advAlcoating2.calculate_R_T()
ax1.plot(lamda*1e9,R,label="Coated Al: 2 repeats")

w,R,T=advAlcoating3.calculate_R_T()
ax1.plot(lamda*1e9,R,label="Coated Al: 3 repeats")

w,R,T=uncoatedAl.calculate_R_T()
ax1.plot(lamda*1e9,R,label="Uncoated Al")

ax1.set_ylim([.6,1])
ax1.set_xlabel("wavelength (nm)")
ax1.set_ylabel("Reflection")
ax1.legend()

P.show()

## bare Al Metal
#uses previously defined thin film object 'uncoatedAl'
#reproducing Freesnell's reproduction of "http://web.archive.org/web/20071011010822/http://www.mellesgriot.com/products/optics/oc_5_1.htm"
ax1 = P.subplot(111)
ax1.set_title("uncoated Aluminum Mirror")

lamda = N.linspace(400e-9,1100e-9,200) # (m) wavelength
wnew = 2*pi*c/lamda # (Hz) frequency (natural)
wnew,R,T=uncoatedAl.calculate_R_T(w=wnew)
ax1.plot(lamda*1e9,R,label="Uncoated Al")

ax1.set_ylim([.75,1])
ax1.set_xlabel("wavelength (nm)")
ax1.set_ylabel("Reflection")
ax1.legend()

P.show()

### Another Al Coating
#Reproduction of Jaffer's reproduction of "http://www.cvimellesgriot.com/Products/Protected-Aluminum-Flat-Mirrors.aspx"
#Si2O3 coating on Al
lamda = N.linspace(400e-9,750e-9,200) # (m) wavelength
w = 2*pi*c/lamda # (Hz) frequency (natural)

Si2O3 = 1.65 #refractive indices
#SrF2 = 1.4 #
  
nom = 550e-9

Si2O3Alcoating = TM.Filter(
            [Layer(1.0,None),
            Layer(Si2O3, 0.5*nom/Si2O3),
            Layer(Al,None)],
            w=w,
            pol='TM',
            theta=0.0)

ax1 = P.subplot(111)
ax1.set_title("Si2O3 Protected Aluminum (/011)")

w,R,T=Si2O3Alcoating.calculate_R_T()
ax1.plot(lamda*1e9,R,label="Si2O3 Coated Al: 0deg")

w,R,T=Si2O3Alcoating.calculate_R_T(theta=pi/4)
ax1.plot(lamda*1e9,R,label="Si2O3 Coated Al: 45deg p-pol")
w,R,T=Si2O3Alcoating.calculate_R_T(theta=pi/4,pol='TE')
ax1.plot(lamda*1e9,R,label="Si2O3 Coated Al: 45deg p-pol")


#w,R,T=uncoatedAl.calculate_R_T(w=w)
#ax1.plot(lamda*1e9,R,label="Uncoated Al: 0deg")

#w,R,T=uncoatedAl.calculate_R_T(theta=pi/4,w=w)
#ax1.plot(lamda*1e9,R,label="Uncoated Al: 45deg")
#w,R,T=uncoatedAl.calculate_R_T(theta=pi/4,pol='TE',w=w)
#ax1.plot(lamda*1e9,R,label="Uncoated Al: 45deg")

ax1.set_ylim([.7,1])
ax1.set_xlabel("wavelength (nm)")
ax1.set_ylabel("Reflection")
ax1.legend(loc=8)

P.show()

## Gold (Au)
#reproducing Freesnell's reproduction of "http://www.cvimellesgriot.com/Products/Bare-Gold-and-Protected-Gold-Flat-Mirrors.aspx"

lamda = N.linspace(.4e-6,24e-6,200) # (m) wavelength
#w = 2*pi*c/lamda # (Hz) frequency (natural)
uncoatedAu =  TM.Filter(
            [Layer(1.0,None),
            Layer(Au,None)],
            w=2*pi*c/lamda) # pol = 'TE' and theta=0.0 by default
w,R,T=uncoatedAu.calculate_R_T()

ax1 = P.subplot(111)
ax1.set_title("Bare Gold (/45)")
ax1.plot(lamda*1e6,R,label="Uncoated Al")
ax1.set_ylim([0,1])
ax1.set_xlabel("wavelength (um)")
ax1.set_ylabel("Reflection")
P.show()


### Thin Metal Layers
#Reproduction of Jaffer's reproduction of "http://www.sspectra.com/designs/mdbp.html"
#Si2O3 coating on Al
lamda = N.linspace(.7e-6,1e-6,200) # (m) wavelength
w = 2*pi*c/lamda # (Hz) frequency (natural)

SiO2 = 1.4 #refractive index
TiO2 = 2.45
BK7 = 1.5164
#Au = 1.693+1.883j

metal_bp = TM.Filter(
            [Layer(1.0,None),
            Layer(TiO2,101.94e-9),
    	    Layer(Au,24.97e-9),
    	    Layer(SiO2,127.87e-9),
    	    Layer(TiO2,94.24e-9),
    	    Layer(SiO2,302.57e-9),
    	    Layer(TiO2,94.24e-9),
    	    Layer(SiO2,121.94e-9),
    	    Layer(Au,23.33e-9),
            Layer(BK7,None)],
            w=w,
            pol='TE',
            theta=0.0)

ax1 = P.subplot(111)
ax1.set_title("Metal-Dielectric Bandpass Filter")

scalefactor=1e6
w,R,T=metal_bp.calculate_R_T()
ax1.plot(lamda*scalefactor,T,label="metal-dielectric bandpass")

ax1.arrow(8.70e-7*scalefactor, 0, 0.0, 0.5, head_width=0.01, head_length=0.05, fc='k', ec='k')

ax1.set_ylim([0,1])
ax1.set_xlabel("wavelength (um)")
ax1.set_ylabel("Transmission")
#ax1.legend(loc=8)

P.show()


### Thin Metal Layers #2
#Reproduction of Jaffer's reproduction of "http://www.sspectra.com/designs/mdbp2.html"
#Si2O3 coating on Al
lamda = N.linspace(.7e-6,1e-6,200) # (m) wavelength
w = 2*pi*c/lamda # (Hz) frequency (natural)

SiO2 = 1.4 #refractive index
TiO2 = 2.4
BK7 = 1.5164
#Au = 1.693+1.883i

dual_bp = TM.Filter(
            [Layer(1.0,None),
    	    Layer(Au,10.76e-9),
    	    Layer(SiO2,102.01e-9),
    	    Layer(TiO2,95.25e-9),
    	    Layer(SiO2,10.49e-9),
    	    Layer(Au,4.16e-9),
    	    Layer(SiO2,270.66e-9),
    	    Layer(TiO2,93.69e-9),
    	    Layer(SiO2,152.40e-9),
    	    Layer(TiO2,39.24e-9),
    	    Layer(SiO2,49.67e-9),
    	    Layer(TiO2,96.33e-9),
    	    Layer(SiO2,115.39e-9),
    	    Layer(Au,16.58e-9),
            Layer(BK7,None)],
            w=w,
            pol='TM',
            theta=0.0)

ax1 = P.subplot(111)
ax1.set_title("Metal-Dielectric Dual Bandpass Filter")

scalefactor=1e6
w,R,T=dual_bp.calculate_R_T()
ax1.plot(lamda*scalefactor,T,label="metal-dielectric bandpass")

ax1.arrow(.770e-6*scalefactor, 0, 0.0, 0.5, head_width=0.01, head_length=0.05, fc='k', ec='k')
ax1.arrow(.920e-6*scalefactor, 0, 0.0, 0.5, head_width=0.01, head_length=0.05, fc='k', ec='k')

ax1.set_ylim([0,1])
ax1.set_xlabel("wavelength (um)")
ax1.set_ylabel("Transmission")
#ax1.legend(loc=8)

P.show()


