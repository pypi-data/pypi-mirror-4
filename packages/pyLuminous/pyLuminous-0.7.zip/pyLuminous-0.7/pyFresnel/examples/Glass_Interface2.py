#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# This file is part of pyFresnel.
# Copyright (c) 2012, Robert Steed
# Author: Robert Steed (rjsteed@talk21.com)
# License: GPL
# last modified 18.12.2012
import pyFresnelInit
import pylab as pl
import pyFresnel.fresnel as F
pi=pl.pi

f1=pl.figure(1)
ax1=f1.add_subplot(111)
f2=pl.figure(2)
ax2=f2.add_subplot(111)

theta=pl.arange(0.0,90.0,0.2)
theta2=theta*pi/180.0
I=F.Interface(n1=1.5,n2=1.0,theta=theta2)

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

ax1.set_title("Total Internal Reflection of Glass")
ax1.set_xlabel("Angle of incidence (degrees)")
ax1.set_ylabel("Relative field amplitudes")
ax2.set_title("Total Internal Reflection of Glass")
ax2.set_xlabel("Angle of incidence (degrees)")
ax2.set_ylabel("Transmittance/Reflectance")
pl.show()