"""Testing transfer matrix model for an anisotropic anbsorber"""
import pyFresnelInit
from pyFresnel.optical_plate import Plate as Plate0
from pyFresnel.materials import QW_ISBT,Material_nk
from pyFresnel.fresnel import Interface
import pyFresnel.uniaxial_plate2 as aniso
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
w0=1.e12*2*pi # frequency of transition (natural)
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
QW=aniso.AnisoPlate_eps(eps_xx,eps_zz,Lqw,w,theta,eps_b=barrier.epsilon())

######## Transfer Matrix Model

TM0 = TM.Filter([TM.Layer_eps(barrier.epsilon(),None),
		TM.LayerUniaxial_eps(well.epsilon(),ISBT1.epsilon(),Lqw),
                TM.Layer_eps(barrier.epsilon(),None)],
                w=w,
                pol='TM',
                theta=theta)

#theta,TM_r_p,TM_t_p = TM0.calculate_r_t()
w,TM_R_p,TM_T_p = TM0.calculate_R_T()
TM0.pol='TE'
#theta,TM_r_s,TM_t_s = TM0.calculate_r_t()
theta,TM_R_s,TM_T_s = TM0.calculate_R_T()

#########

ax=pl.subplot(111)
ax.set_title("Absorption of a slab containing a type of anisotopic absorber")
#i.e. quantum well intersubband transitions
#thickness of slab is Lqw rather than the more accurate Leff for QW ISBTs
#plots have been roughly normalised

ax.axvline(w0/2/pi)#line for w0
ax.axvline(sqrt(w0**2-y**2)/2/pi)#line for sqrt(w0**2 - y**2)
#ax.plot(f,ISBT1.epsilon().imag*0.0003,label="imaginary epsilon")
#ax.plot(f,w*ISBT1.epsilon().imag/well.n().real/c*Lqw/cos(theta),label="simplified absorption over layer length") #simple absorption for quantum well = w * eps'' / n_background /c
#ax.plot(f,2*w*ISBT1.n().imag/c*Lqw/cos(theta),label="proper absorption over layer length")#absorption in a quantum well 'medium'
#ax.plot(f,1-QWsimplified.T_p(),label="simplified dielectric, absorption in a quantum well slab, thickness Lqw")#absorption of a quantum well 'medium' using simplified dielectric constant
#ax.plot(f,1-QW0.T_p(),label="absorption in a quantum well slab, thickness Lqw") #absorption in a quantum well slab, thickness Lqw
ax.plot(f,1-QW.T_p(),label="Etalon Model")#label="absorption in an anisotopic quantum well slab, thickness Lqw") #absorption in a quantum well slab, thickness Lqw
#ax.axvline(sqrt(w0**2+wp**2)/2/pi)#line for sqrt(w0**2 + wp**2) (using Lqw not Leff)
#ax.axvline(sqrt(w0**2-y**2+wp**2)/2/pi)#line for sqrt(w0**2 - y**2 + wp**2)
ax.axvline(sqrt(w0**2+f12*wp**2)/2/pi)#line for sqrt(w0**2 + f12*wp**2) (using Lqw not Leff)
ax.axvline(sqrt(w0**2-y**2+f12*wp**2)/2/pi)#line for sqrt(w0**2 - y**2 + f12*wp**2)

ax.plot(f,1-TM_T_p,label="Transfer Matrix model,pol TM") #absorption in a quantum well slab, thickness Lqw
ax.plot(f,1-TM_T_s,label="Transfer Matrix model, pol TE") #absorption in a quantum well slab, thickness Lqw

ax.text(1.2e12,0.035,"The peak starts at 1THz but is shifted by\nthe depolarisation effect to a higher frequency")

ax.set_ylim([0,0.05])
ax.set_ylabel("1 - Transmittance")
ax.set_xlabel("Frequency (Hz)")
ax.legend()
pl.show()