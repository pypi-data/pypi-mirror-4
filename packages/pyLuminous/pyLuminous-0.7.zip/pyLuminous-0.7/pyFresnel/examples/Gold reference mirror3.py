import numpy as N
import matplotlib.pyplot as P
import constants as C
pi=N.pi

"""Looking at reflectivity of a gold mirror between 50 - 200 meV at 45degrees. 
Here I am using the dielectric function from Etchegoin 2006"""

import pyFresnelInit
from pyFresnel.fresnel import Interface
import pyFresnel.materials as mat
import pyFresnel.optical_plate as op
gold=mat.Gold
GaAs=mat.GaAs_THz

ax1=P.subplot(211)
ax2=P.subplot(212)
f=N.arange(1e12,60e12,1e10)
w=2*pi*f # natural frequency.
meV=f*C.h*1e3/C.e #meV scale

gold0=gold(w)
#substrate0=gold(w)
substrate0=GaAs(w)

igold=Interface(1.0,gold0.n(),pi/4)
isubstrate=Interface(1.0,substrate0.n(),pi/4)
d=100e-9 #thickness of gold on substrate
gold_mirror=op.Plate(gold0.n(),d,w,theta=pi/4,n0=1.0,n2=substrate0.n())

ax1.plot(meV,igold.R_s(),label="gold s pol")
ax2.plot(meV,igold.R_p(),label="gold p pol")
ax1.plot(meV,isubstrate.R_s(),label="GaAs s pol")
ax2.plot(meV,isubstrate.R_p(),label="GaAs p pol")
ax1.plot(meV,gold_mirror.R_s(),label="gold on GaAs s pol")
ax2.plot(meV,gold_mirror.R_p(),label="gold on GaAs p pol")

ax1.set_xlabel("Energy (meV)")
ax1.set_ylabel("Reflectance")
ax2.set_xlabel("Energy (meV)")
ax2.set_ylabel("Reflectance")
ax1.legend()
ax2.legend()
P.show()