#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# This file is part of pyFresnel.
# Copyright (c) 2012, Robert Steed
# Author: Robert Steed (rjsteed@talk21.com)
# License: GPL
# last modified 18.12.2012
"""Looking at reflectivity of a gold mirror between 0 - 3 THz at 45degrees. 
The real gold mirror is a coating on a piece of silicon and therefore will have 
a lower conductivity than bulk gold. we are also interested in the change of 
reflectivity between 4K and 300K. For example bulk gold conductivity is 45.2E6 
(Ohms**-1 m**-1) at 300K and 208E6 at 80K."""

import numpy as N
import matplotlib.pyplot as P
pi=N.pi

import pyFresnelInit
from pyFresnel.fresnel import Interface
import pyFresnel.materials as mat
import pyFresnel.optical_plate as op
Metal2=mat.Metal2

ax1=P.subplot(211)
ax2=P.subplot(212)
f=N.arange(1e10,3e12,1e10)
w=2*pi*f # natural frequency
fax=f*1e-12

gold300K=Metal2(w,45.2E6,2*pi*3.6e12,1.0) #(45.2E6,1.0)
gold80K=Metal2(w,208E6,2*pi*3.6e12,1.0) #(208E6,1.0)

i300K=Interface(1.0,gold300K.n(),pi/4)
i80K=Interface(1.0,gold80K.n(),pi/4)
d=50e-9 #thickness of gold on silicon substrate
gold_silicon300K=op.Plate(gold300K.n(),d,w,theta=pi/4,n0=1.0,n2=3.45)
gold_silicon80K=op.Plate(gold80K.n(),d,w,theta=pi/4,n0=1.0,n2=3.45)

#ax1.plot(fax,i300K.R_s(),label="300K s pol")
#ax1.plot(fax,i300K.R_p(),label="300K p pol")
ax1.plot(fax,gold_silicon300K.R_s(),label="300K s pol si substr")
ax1.plot(fax,gold_silicon300K.R_p(),label="300K s pol si substr")

#ax1.plot(fax,i80K.R_s(),label="80K s pol")
#ax1.plot(fax,i80K.R_p(),label="80K p pol")
ax1.plot(fax,gold_silicon80K.R_s(),label="80K s pol si substr")
ax1.plot(fax,gold_silicon80K.R_p(),label="80K s pol si substr")

#ax2.plot(fax,i300K.R_s()/i80K.R_s(),label="300K/80K s pol")
#ax2.plot(fax,i300K.R_p()/i80K.R_p(),label="300K/80K p pol")
ax2.plot(fax,gold_silicon300K.R_s()/gold_silicon80K.R_s(),label="300K/80K s pol si substr")
ax2.plot(fax,gold_silicon300K.R_p()/gold_silicon80K.R_p(),label="300K/80K p pol si substr")

ax1.set_xlabel("Frequency (THz)")
ax1.set_ylabel("Reflectance")
ax2.set_xlabel("Frequency (THz)")
ax2.set_ylabel("Fractional Change in Reflectivity")
ax1.legend()
ax2.legend()
P.show()