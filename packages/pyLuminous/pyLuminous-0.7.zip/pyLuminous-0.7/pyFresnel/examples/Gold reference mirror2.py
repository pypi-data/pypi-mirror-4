import numpy as N
import matplotlib.pyplot as P
pi=N.pi

"""Looking at reflectivity of a gold mirror between 0 - 20 THz at 45degrees. 
The real gold mirror is a coating on a piece of GaAs or Silicon and therefore 
will have a lower conductivity than bulk gold. we are also interested in the 
change of reflectivity between 4K and 300K. For example bulk gold conductivity 
is 45.2E6 (Ohms**-1 m**-1) at 300K and 208 at 80K. Here, I am using the dielectric
constants that Yanko uses in his smatrix program."""

import pyFresnelInit
from pyFresnel.fresnel import Interface
import pyFresnel.materials as mat
import pyFresnel.optical_plate as op
gold=mat.Gold_THz
GaAs=mat.GaAs_THz

ax1=P.subplot(211)
ax2=P.subplot(212)
f=N.arange(1e10,20e12,1e10)
w=2*pi*f # natural frequency.

gold0=gold(w)
GaAs0=GaAs(w)

print GaAs0.n()


igold=Interface(1.0,gold0.n(),pi/4)
iGaAs=Interface(1.0,GaAs0.n(),pi/4)
d=20e-9 #thickness of gold on silicon substrate
gold_GaAs=op.Plate(gold0.n(),d,w,theta=pi/4,n0=1.0,n2=GaAs0.n())

fax=f*1e-12
ax1.plot(fax,igold.R_s(),label="gold s pol")
ax2.plot(fax,igold.R_p(),label="gold p pol")
ax1.plot(fax,iGaAs.R_s(),label="GaAs s pol")
ax2.plot(fax,iGaAs.R_p(),label="GaAs p pol")
ax1.plot(fax,gold_GaAs.R_s(),label="gold on GaAs s pol")
ax2.plot(fax,gold_GaAs.R_p(),label="gold on GaAs p pol")

ax1.set_xlabel("Frequency (THz)")
ax1.set_ylabel("Reflectance")
ax2.set_xlabel("Frequency (THz)")
ax2.set_ylabel("Reflectance")
ax1.legend()
ax2.legend()
P.show()