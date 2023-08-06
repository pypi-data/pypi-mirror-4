"""Testing the Transfer matrix code for isotropic absorbing medium"""
import pyFresnelInit
from pyFresnel.optical_plate import Plate
from pyFresnel.materials import QW_ISBT,Material_nk
#from pyFresnel.fresnel import Interface
import pyFresnel.transfer_matrix as TM

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
well=Material_nk(3.585) # refractive index of GaAs
barrier=Material_nk(3.585) # refractive index of AlGaAs

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

QW=Plate(ISBT1.n(),Lqw,w,theta,n0=barrier.n(),n2=barrier.n())

######### Code for Slab

ax=pl.subplot(111)
#plots have been roughly normalised

ax.axvline(w0/2/pi)#line for w0
ax.axvline(sqrt(w0**2-y**2)/2/pi)#line for sqrt(w0**2 - y**2)
#ax.plot(f,ISBT1.epsilon().imag*0.0003,label="imaginary epsilon")
#ax.plot(f,w*ISBT1.epsilon().imag/well.n().real/c*Lqw/cos(theta),label="simplified absorption over layer length") #simple absorption for quantum well = w * eps'' / n_background /c
#ax.plot(f,2*w*ISBT1.n().imag/c*Lqw/cos(theta),label="proper absorption over layer length")#absorption in a quantum well 'medium'
ax.plot(f,1-QW.T_p(),label="absorption in a quantum well slab, thickness Lqw") #absorption in a quantum well slab, thickness Lqw
#ax.axvline(sqrt(w0**2+wp**2)/2/pi)#line for sqrt(w0**2 + wp**2) (using Lqw not Leff)
#ax.axvline(sqrt(w0**2-y**2+wp**2)/2/pi)#line for sqrt(w0**2 - y**2 + wp**2)
ax.axvline(sqrt(w0**2+f12*wp**2)/2/pi)#line for sqrt(w0**2 + f12*wp**2) (using Lqw not Leff)
ax.axvline(sqrt(w0**2-y**2+f12*wp**2)/2/pi)#line for sqrt(w0**2 - y**2 + f12*wp**2)

######### Code for Transfer Matrix Model of slab

f1 = TM.Filter([TM.Layer_eps(barrier.epsilon(),None),
                TM.Layer_eps(ISBT1.epsilon(),Lqw),
                TM.Layer_eps(barrier.epsilon(),None)],
                w=w,
                pol='TM',
                theta=theta)

TM_T = f1.calculate_R_T()[2]
ax.plot(f,1 - TM_T,'--',label="Transfer Matrix Absorption in a QW slab, thickness Lqw")

#########
ax.set_ylim([0,0.05])
ax.set_xlabel("Frequency (Hz)")
ax.set_ylabel("1 - Transmission")
ax.legend()
pl.show()