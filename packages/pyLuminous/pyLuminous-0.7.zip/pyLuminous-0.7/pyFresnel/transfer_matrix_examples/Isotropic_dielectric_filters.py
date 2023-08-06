"""Testing the isotropic part of the transfer matrix class using the dielectric
tests from Freesnell. See the Freesnell website for details."""

import pyFresnelInit
import pyFresnel.transfer_matrix as TM
Layer=TM.Layer
import numpy as N
import matplotlib.pyplot as P
pi=N.pi
c=299792458  #m/s - speed of light

### Wide-bp
#jaffer was reproducing "http://www.sspectra.com/designs/irbp.html"
lamda = N.linspace(2e-6,7e-6,300) # (m) wavelength
w = 2*pi*c/lamda # (Hz) frequency (natural)

ZnS = 2.2 # refractive index
Ge = 4.2 # refractive index
    
wide_bp = TM.Filter(
            [Layer(1.0,None),
            Layer(ZnS,528.64e-9),
            Layer(Ge,178.96e-9),
            Layer(ZnS,250.12e-9),
            Layer(Ge,123.17e-9),
            Layer(ZnS,294.15e-9),
            Layer(Ge,156.86e-9),
            Layer(ZnS,265.60e-9),
            Layer(Ge,134.34e-9),
            Layer(ZnS,266.04e-9),
            Layer(Ge,147.63e-9),
            Layer(ZnS,289.60e-9),
            Layer(Ge,133.04e-9),
            Layer(ZnS,256.22e-9),
            Layer(Ge,165.16e-9),
            Layer(ZnS,307.19e-9),
            Layer(Ge,125.25e-9),
            Layer(ZnS,254.28e-9),
            Layer(Ge,150.14e-9),
            Layer(ZnS,168.55e-9),
            Layer(Ge, 68.54e-9),
            Layer(ZnS,232.65e-9),
            Layer(Ge,125.48e-9),
            Layer(ZnS,238.01e-9),
            Layer(Ge,138.25e-9),
            Layer(ZnS,268.21e-9),
            Layer(Ge, 98.28e-9),
            Layer(ZnS,133.58e-9),
            Layer(Ge,125.31e-9),
            Layer(ZnS,224.72e-9),
            Layer(Ge, 40.79e-9),
            Layer(ZnS,564.95e-9),
            Layer(Ge,398.52e-9),
            Layer(ZnS,710.47e-9),
            Layer(Ge,360.01e-9),
            Layer(ZnS,724.86e-9),
            Layer(Ge,353.08e-9),
            Layer(ZnS,718.52e-9),
            Layer(Ge,358.23e-9),
            Layer(ZnS,709.26e-9),
            Layer(Ge,370.42e-9),
            Layer(ZnS,705.03e-9),
            Layer(Ge,382.28e-9),
            Layer(ZnS,720.06e-9),
            Layer(Ge,412.85e-9),
            Layer(ZnS,761.47e-9),
            Layer(Ge, 48.60e-9),
            Layer(ZnS,97.33e-9),
            Layer(4.0,None)],
            w=w,
            pol='TM',
            theta=0.0)

w,R,T=wide_bp.calculate_R_T()
#w,R2,T2=wide_bp.calculate_R_T(pol='TE')
        
ax1 = P.subplot(111)
#ax1.plot(lamda,R,label="TM Reflection")
ax1.plot(lamda,T,label="Transmission")
#ax1.plot(lamda,R2,label="TE Reflection")
#ax1.plot(lamda,T2,label="TE Transmission")
ax1.set_xlabel("Wavelength (m)")
ax1.set_ylabel("Transmission")
ax1.set_title("Wide Infrared Bandpass Filter")
#ax1.legend()

P.show()


##### anti
#jaffer was reproducing "http://www.sspectra.com/designs/IR_AR.html"
lamda = N.linspace(7700e-9,12300e-9,300) # (m) wavelength
w = 2*pi*c/lamda # (Hz) frequency (natural)

L = 2.2 # refractive index
H = 4.2 # refractive index

anti = TM.Filter(
                [Layer(1.0,None),
                Layer(L,1076.97e-9),
                Layer(H,629.03e-9),
                Layer(L,457.49e-9),
                Layer(H,131.55e-9),
                Layer(L,1234.92e-9),
                Layer(H,1142.59e-9),
                Layer(L,2590.54e-9),
                Layer(H,81.75e-9),
                Layer(L,1827.50e-9),
                Layer(H,84.60e-9),
                Layer(L,563.34e-9),
                Layer(H,285.97e-9),
                Layer(L,157.14e-9),
                Layer(4.0,None)],
                w=w,
                pol='TM',
                theta=0.0)
                
                
w,R,T=anti.calculate_R_T()
#w,R2,T2=anti.calculate_R_T(pol='TE')
        
ax1 = P.subplot(111)
ax1.plot(lamda,R,label="TM Reflection")
#ax1.plot(lamda,T,label="Transmission")
#ax1.plot(lamda,R2,label="TE Reflection")
#ax1.plot(lamda,T2,label="TE Transmission")
ax1.set_xlabel("Wavelength (m)")
ax1.set_ylabel("Reflection")
ax1.set_title("Growing an Antireflection Coating")
#ax1.legend()

P.show()

##### immersed
#jaffer was reproducing "http://www.sspectra.com/designs/immersedWPol.html"
angles = N.linspace(51,71,50) # angles (degrees)
lamda = .653e-6 # (m) wavelength
w = 2*pi*c/lamda # (Hz) frequency (natural)

SiO2 = 1.45 # refractive index
TiO2 = 2.35 # refractive index
BK7 = 1.5164

anti = TM.Filter(
                [Layer(BK7,None),
                Layer(TiO2,83.62e-9),
                Layer(SiO2,74.91e-9),
                Layer(TiO2,94.86e-9),
    		Layer(SiO2,119.09e-9),
    		Layer(TiO2,90.21e-9),
    		Layer(SiO2,129.48e-9),
    		Layer(TiO2,81.87e-9),
    		Layer(SiO2,123.04e-9),
    		Layer(TiO2,84.03e-9),
    		Layer(SiO2,138.23e-9),
    		Layer(TiO2,81.34e-9),
    		Layer(SiO2,131.15e-9),
    		Layer(TiO2,83.85e-9),
    		Layer(SiO2,152.21e-9),
    		Layer(TiO2,80.48e-9),
    		Layer(SiO2,126.78e-9),
    		Layer(TiO2,59.95e-9),
                Layer(BK7,None)],
                w=w,
                pol='TM',
                theta=angles*pi/180.0)

ax1 = P.subplot(111)
for lam in .653e-6,.643e-6,.633e-6,.623e-6,.613e-6:
    w = 2*pi*c/lam # (Hz) frequency (natural)                
    angles_rad,R,T=anti.calculate_R_T(w=w)
    #w,R2,T2=anti.calculate_R_T(pol='TE')
        
    #ax1.plot(lamda,R,label="TM Reflection")
    ax1.plot(angles,T,label="Transmission")
    #ax1.plot(lamda,R2,label="TE Reflection")
    #ax1.plot(lamda,T2,label="TE Transmission")

ax1.set_ylim([0.9,1])
ax1.set_xlim([51,71])
ax1.set_xlabel("Incidence (degrees)")
ax1.set_ylabel("Transmission")
ax1.set_title("Immersed Wide-Angle Polarizer")
#ax1.legend()

P.show()


##### Prism
# jaffer was reproducing "http://www.sspectra.com/designs/ftr_polar.html"
lamda = N.linspace(.4e-6,.7e-6,50) # (m) wavelength
w = 2*pi*c/lamda # (Hz) frequency (natural)

H = 2.35 # refractive index
L = 1.45 # refractive index

prism = TM.Filter(
            [Layer(1.85,None),
            Layer(H,11.16e-9),
	    Layer(L,48.87e-9),
	    Layer(H,35.94e-9),
	    Layer(L,68.58e-9),
	    Layer(H,39.50e-9),
	    Layer(L,79.77e-9),
	    Layer(H,46.20e-9),
	    Layer(L,96.61e-9),
	    Layer(H,49.71e-9),
	    Layer(L,102.74e-9),
	    Layer(H,50.49e-9),
	    Layer(L,102.74e-9),
	    Layer(H,49.71e-9),
	    Layer(L,96.61e-9),
	    Layer(H,46.20e-9),
	    Layer(L,79.77e-9),
	    Layer(H,39.50e-9),
	    Layer(L,68.58e-9),
	    Layer(H,35.94e-9),
	    Layer(L,48.87e-9),
	    Layer(H,11.16e-9),
            Layer(1.85,None)],
            w=w,
            pol='TM',
            theta=65*pi/180.0)

ax1 = P.subplot(211)
ax1.set_title("New Thin Film Polarizing Beamsplitter - S")
ax2 = P.subplot(212)
ax2.set_title("New Thin Film Polarizing Beamsplitter - P")


for ang in range(65,76):
    w,R,T=prism.calculate_R_T(theta=ang*pi/180.0,pol='TE')
    ax1.plot(lamda,T,label="Transmission TE at %f deg" %ang)
    
    w,R2,T2=prism.calculate_R_T(theta=ang*pi/180.0,pol='TM')
    T2dB = 10.0*N.log10(T2)
    ax2.plot(lamda,T2dB,label="Transmission TM at %f def" %ang)

ax1.set_ylim([0.99,1])
ax1.set_xlabel("wavelength (m)")
ax1.set_ylabel("Transmission")
ax2.set_ylabel("Transmission (dB)")
#ax1.legend()

P.show()

del ax2
#### Optilayer - fig. 2.2 - antireflection coating?
#jaffer was reproducing
"""#Sh. A. Furman and A. V. Tikhonravov.
#Basics of Optics of Multilayer Systems.
#Editions Fronti`eres, Gif-sur-Yvette Cedex -- France, 1992.
#http://www.optilayer.com/cgi-bin/od/odn.pl?ID=2

#Fig. 2.2: Reflectances of the 6-layer antireflection coatings
#with nS = 1.52, nH = 2.30, nL = 1.45 (lambda = 500nm)
# (1)6S .318H .34L 1.977H .106L .375H 1.099L,
# (2)6S .34H .391L 1.104H .188L .710H 1.216L
"""
lamda = N.linspace(400e-9,900e-9,200) # (m) wavelength
w = 2*pi*c/lamda # (Hz) frequency (natural)

nH = 2.30 # refractive index
nL = 1.45 # refractive index
nS = 1.52

d=500e-9/4.0
fig22a = TM.Filter(
            [Layer(1.0,None),
            Layer(nL,1.099*d/nL),
            Layer(nH,0.375*d/nH),
            Layer(nL,0.106*d/nL),
            Layer(nH,1.977*d/nH),
            Layer(nL,0.34*d/nL),
            Layer(nH,0.318*d/nH),
            Layer(nS,None)],
            w=w,
            pol='TM',
            theta=0.0)

fig22b = TM.Filter(
            [Layer(1.0,None),
            Layer(nL,1.216*d/nL),
            Layer(nH,0.710*d/nH),
            Layer(nL,0.188*d/nL),
            Layer(nH,1.104*d/nH),
            Layer(nL,0.391*d/nL),
            Layer(nH,0.34*d/nH),
            Layer(nS,None)],
            w=w,
            pol='TM',
            theta=0.0)

ax1 = P.subplot(111)
ax1.set_title("fig-2.2")

w,R,T=fig22a.calculate_R_T()
ax1.plot(lamda,R,label="Transmission of filter 1")

w,R2,T2=fig22b.calculate_R_T()
ax1.plot(lamda,R2,label="Transmission of filter 2")

ax1.set_ylim([0.0,0.02])
ax1.set_xlabel("wavelength (m)")
ax1.set_ylabel("Transmission")
ax1.legend()

P.show()

#### Optilayer - 8 layer antireflection coating
#jaffer was reproducing
"""#Fig. 2.5: Reflectance of the 8-layer antireflection coating
#with nS = 1.52, nH = 2.30, nL = 1.38 (lambda = 500nm)
#  8S .295H .291L .149H .074L 1.915H ?? .107H 1.052L
#The geometric thicknesses of the layers in nanometers
#(starting from the substrate) are equal to
#14.1; 26.4; 8.1; 6.7; 104.1; 9.7; 16.9; 95.3.
#The optical thicknesses of the layers are equal to
#32.4; 36.4; 18.6; 9.3; 239.4; 13.4; 38.9; 131.5.
"""
lamda = N.linspace(400e-9,800e-9,200) # (m) wavelength
w = 2*pi*c/lamda # (Hz) frequency (natural)

nH = 2.30 # refractive index
nL = 1.38 # refractive index
nS = 1.52

fig25 = TM.Filter(
            [Layer(1.0,None),
            Layer(nL,95.3e-9),
            Layer(nH,16.9e-9),
            Layer(nL,9.7e-9),
            Layer(nH,104.1e-9),
            Layer(nL,6.7e-9),
            Layer(nH,8.1e-9),
            Layer(nL,26.4e-9),
            Layer(nH,14.1e-9),
            Layer(nS,None)],
            w=w,
            pol='TM',
            theta=0.0)


ax1 = P.subplot(111)
ax1.set_title("fig 2.5")

w,R,T=fig25.calculate_R_T()
ax1.plot(lamda,R,label="Transmission of 8 layer antireflection filter")

ax1.set_ylim([0.0,0.004])
ax1.set_xlabel("wavelength (m)")
ax1.set_ylabel("Transmission")
ax1.legend()

P.show()

##### HL7
#Jaffer was reproducing "http://www.kruschwitz.com/HR%27s.htm#The Basic HR"
lamda = N.linspace(400e-9,700e-9,200) # (m) wavelength
w = 2*pi*c/lamda # (Hz) frequency (natural)

glass = 1.52 #refractive index.
SiO2 = 1.46
TiO2 = 2.40

HL7list = [Layer(1,None),
        Layer(TiO2,0.25),
        Layer(SiO2,0.25),
        Layer(TiO2,0.25),
        Layer(SiO2,0.25),
        Layer(TiO2,0.25),
        Layer(SiO2,0.25),
        Layer(TiO2,0.25),
        Layer(SiO2,0.25),
        Layer(TiO2,0.25),
        Layer(SiO2,0.25),
        Layer(TiO2,0.25),
        Layer(SiO2,0.25),
        Layer(TiO2,0.25),
        Layer(SiO2,0.25),
        Layer(TiO2,0.25),
        Layer(glass,None)]

#convert optical thicknesses to real thicknesses
for layer in HL7list[1:-1]: layer.d *= 550e-9/layer._n

HL7 = TM.Filter(
            HL7list,
            w=w,
            pol='TM',
            theta=0.0)

ax1 = P.subplot(111)
ax1.set_title("(HL)^7H on glass")

w,R,T=HL7.calculate_R_T()
ax1.plot(lamda*1e9,R,label="Reflection")

ax1.set_ylim([0.99,1.0])
ax1.set_xlabel("wavelength (nm)")
ax1.set_ylabel("Reflection")
#ax1.legend()

P.show()


### Cold Mirror
#Jaffer was reproducing "http://www.kruschwitz.com/Cold/hot.htm"
lamda = N.linspace(300e-9,1100e-9,200) # (m) wavelength
w = 2*pi*c/lamda # (Hz) frequency (natural)

glass = 1.52 #refractive index.
SiO2 = 1.46
TiO2 = 2.40

d=550e-9
    
def cm_unit(d):
    return [Layer(TiO2,1./8 * d/TiO2),
            Layer(SiO2,1./4 * d/SiO2),
            Layer(TiO2,1./8 * d/TiO2)]
    
cold_mirror_list = [Layer(1,None),
        Layer(SiO2,0.5 * d / SiO2)]+ \
        5*cm_unit(0.8*d) + \
        5*cm_unit(d)     + \
        5*cm_unit(1.2*d) + \
        [Layer(glass,None)]

cold_mirror = TM.Filter(
            cold_mirror_list,
            w=w,
            pol='TM',
            theta=0.0)

ax1 = P.subplot(111)
ax1.set_title("Cold Mirror")

w,R,T=cold_mirror.calculate_R_T()
ax1.plot(lamda*1e9,R,label="Reflection")

ax1.set_xlabel("wavelength (nm)")
ax1.set_ylabel("Reflection")
#ax1.legend()

P.show()

  
### Cold Mirrors
#Jaffer was reproducing "http://www.sspectra.com/designs/coldmirror.html"
#and "http://www.sspectra.com/designs/coldmirror2.gif"
lamda = N.linspace(380e-9,1000e-9,200) # (m) wavelength
w = 2*pi*c/lamda # (Hz) frequency (natural)

glass = 1.52 #refractive index.
SiO2 = 1.46
TiO2 = 2.40

cold_mirror1 = TM.Filter(
            [Layer(1.0,None),
            Layer(TiO2,34.40e-9),
            Layer(SiO2,158.61e-9),
            Layer(TiO2,53.24e-9),
    	    Layer(SiO2,128.87e-9),
    	    Layer(TiO2,67.77e-9),
    	    Layer(SiO2,102.19e-9),
    	    Layer(TiO2,79.13e-9),
    	    Layer(SiO2,97.19e-9),
    	    Layer(TiO2,53.07e-9),
    	    Layer(SiO2,162.54e-9),
    	    Layer(TiO2,36.16e-9),
    	    Layer(SiO2,66.56e-9),
    	    Layer(TiO2,46.48e-9),
    	    Layer(SiO2,87.18e-9),
    	    Layer(TiO2,48.92e-9),
    	    Layer(SiO2,82.52e-9),
    	    Layer(TiO2,42.56e-9),
    	    Layer(SiO2,73.13e-9),
    	    Layer(TiO2,43.97e-9),
    	    Layer(SiO2,102.57e-9),
    	    Layer(TiO2,44.21e-9),
            Layer(glass,None)],
            w=w,
            pol='TM',
            theta=0.0)
            

lamda2 = N.linspace(380e-9,2000e-9,200) # (m) wavelength
w2 = 2*pi*c/lamda2 # (Hz) frequency (natural)

cold_mirror2 = TM.Filter(
            [Layer(1.0,None),
    	    Layer(TiO2,19.03e-9),
    	    Layer(SiO2,191.13e-9),
    	    Layer(TiO2,51.30e-9),
    	    Layer(SiO2,137.38e-9),
    	    Layer(TiO2,61.86e-9),
    	    Layer(SiO2,99.64e-9),
    	    Layer(TiO2,81.48e-9),
    	    Layer(SiO2,102.08e-9),
    	    Layer(TiO2,53.15e-9),
    	    Layer(SiO2,162.37e-9),
    	    Layer(TiO2,36.85e-9),
    	    Layer(SiO2,70.41e-9),
    	    Layer(TiO2,39.55e-9),
    	    Layer(SiO2,88.77e-9),
    	    Layer(TiO2,51.97e-9),
    	    Layer(SiO2,86.41e-9),
    	    Layer(TiO2,51.05e-9),
    	    Layer(SiO2,66.36e-9),
    	    Layer(TiO2,28.39e-9),
    	    Layer(SiO2,124.04e-9),
    	    Layer(TiO2,33.76e-9),
            Layer(glass,None)],
            w=w2,
            pol='TM',
            theta=0.0)

ax1 = P.subplot(111)
ax1.set_title("Cold Mirrors")

w,R,T=cold_mirror1.calculate_R_T()
ax1.plot(lamda*1e9,R,label="Mirror 1")

w2,R2,T2=cold_mirror2.calculate_R_T()
ax1.plot(lamda2*1e9,R2,label="Mirror 2")

ax1.set_xlabel("wavelength (nm)")
ax1.set_ylabel("Reflection")
ax1.legend()

P.show()

## Reflector 50deg
#Reproduction of Jaffer's reproduction of http://www.sspectra.com/designs/bbhr.html
lamda = N.linspace(.4e-6,.8e-6,200) # (m) wavelength
w = 2*pi*c/lamda # (Hz) frequency (natural)

#refractive indices.
L = 1.45
H = 2.35
glass = 1.52

ref50list = [Layer(1,None),
          Layer(H,49.35e-9),
          Layer(L,80.64e-9),
          Layer(H,45.96e-9),
          Layer(L,91.80e-9),
          Layer(H,51.59e-9),
          Layer(L,86.62e-9),
          Layer(H,46.16e-9),
          Layer(L,90.92e-9),
          Layer(H,53.49e-9),
          Layer(L,94.22e-9),
          Layer(H,46.62e-9),
          Layer(L,82.60e-9),
          Layer(H,52.26e-9),
          Layer(L,101.16e-9),
          Layer(H,56.86e-9),
          Layer(L,101.69e-9),
          Layer(H,63.51e-9),
          Layer(L,121.69e-9),
          Layer(H,61.47e-9),
          Layer(L,111.11e-9),
          Layer(H,63.21e-9),
          Layer(L,121.61e-9),
          Layer(H,71.53e-9),
          Layer(L,113.89e-9),
          Layer(H,55.42e-9),
          Layer(L,104.04e-9),
          Layer(H,69.96e-9),
          Layer(L,137.71e-9),
          Layer(H,71.17e-9),
          Layer(L,141.89e-9),
          Layer(H,82.96e-9),
          Layer(L,141.64e-9),
          Layer(H,85.36e-9),
          Layer(L,129.75e-9),
          Layer(H,72.02e-9),
          Layer(L,178.45e-9),
          Layer(H,83.10e-9),
          Layer(L,154.04e-9),
          Layer(H,74.35e-9),
          Layer(L,152.15e-9),
          Layer(H,80.56e-9),
          Layer(L,171.35e-9),
          Layer(H,97.87e-9),
        Layer(glass,None)]

ref50 = TM.Filter(
            ref50list,
            w=w,
            pol='TM',
            theta=50.0*pi/180.0)

ax1 = P.subplot(111)
ax1.set_title("Broadband High-Reflection Coating at 50 Degrees")

w,R,T=ref50.calculate_R_T()
ax1.plot(lamda*1e9,R,label="Reflection")

ax1.set_ylim([0.8,1.0])
ax1.set_xlabel("wavelength (nm)")
ax1.set_ylabel("Reflection")
#ax1.legend()

P.show()

#### Omnirflector
#Reproduction of Jaffer's reproduction of http://www.sspectra.com/designs/omnirefl.html
lamda = N.linspace(6e-6,20e-6,200) # (m) wavelength
w = 2*pi*c/lamda # (Hz) frequency (natural)

#refractive indices.
L = 1.6 #polystyrene
H = 4.6 #tellurium
glass = 1.5442

omnimirror = TM.Filter(
            [Layer(1,None),
            Layer(H,399.00e-9),
            Layer(L,2165.33e-9),
            Layer(H,696.76e-9),
            Layer(L,2097.40e-9),
            Layer(H,701.51e-9),
            Layer(L,2089.58e-9),
            Layer(H,700.83e-9),
            Layer(L,2112.33e-9),
            Layer(H,691.88e-9),
            Layer(glass,None)],
            w=w,
            pol='TM',
            theta=0.0)

ax1 = P.subplot(111)
ax1.set_title("Dielectric Omnidirectional Reflector")

for angle in range(0,90,10)+[89]:
    w,R,T=omnimirror.calculate_R_T(theta=angle*pi/180.0,pol='TM')
    ax1.plot(lamda*1e6,R,'b',label="%g degs" %angle)
    w,R2,T2=omnimirror.calculate_R_T(theta=angle*pi/180.0,pol='TE')
    ax1.plot(lamda*1e6,R2,'r',label="%g degs" %angle)

#ax1.set_ylim([0.8,1.0])
ax1.set_xlabel("wavelength (um)")
ax1.set_ylabel("Reflection")
#ax1.legend()

P.show()
