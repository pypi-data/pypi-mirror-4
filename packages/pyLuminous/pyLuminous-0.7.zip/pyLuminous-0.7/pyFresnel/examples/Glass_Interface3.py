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
ax1=f1.add_subplot(211)
ax1b=f1.add_subplot(212)
f2=pl.figure(2)
ax2=f2.add_subplot(111)

theta=pl.arange(0.0,90.0,0.01)
theta2=theta*pi/180.0
I=F.Interface(n1=1.5,n2=1.0,theta=theta2)

def debounce(a):
    a[a<-pi+1e-4]=pi
    return a

y1=I.r_s(); y2=I.r_p(); y3=I.t_s(); y4=I.t_p()
ax1.plot(theta,abs(y1),label="r_s modulus")
ax1.plot(theta,abs(y2),label="r_p modulus")
ax1.plot(theta,abs(y3),label="t_s modulus")
ax1.plot(theta,abs(y4),label="t_p modulus")

ax1b.plot(theta,debounce(-pl.angle(y1)),label="r_s phase")
ax1b.plot(theta,debounce(-pl.angle(y2)),label="r_p phase")
ax1b.plot(theta,debounce(-pl.angle(y3)),label="t_s phase")
ax1b.plot(theta,debounce(-pl.angle(y4)),label="t_p phase")

ax1b.plot(theta,debounce(-pl.angle(y2))-debounce(-pl.angle(y1)),label="Phase difference")

ax1.legend()
ax1b.legend()

ax2.plot(theta,I.R_s(),label="R_s")
ax2.plot(theta,I.R_p(),label="R_p")
ax2.plot(theta,I.T_s(),label="T_s")
ax2.plot(theta,I.T_p(),label="T_p")
ax2.legend()

ax1.set_title("Total Internal Reflection of Glass")
ax1.set_xlabel("Angle of incidence (degrees)")
ax1.set_ylabel("Relative field amplitudes")
ax1b.set_xlabel("Angle of incidence (degrees)")
ax1b.set_ylabel("Phase Changes")
ax2.set_title("Total Internal Reflection of Glass")
ax2.set_xlabel("Angle of incidence (degrees)")
ax2.set_ylabel("Transmittance/Reflectance")
pl.show()