#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# This file is part of pyFresnel.
# Copyright (c) 2013, Robert Steed
# Author: Robert Steed (rjsteed@talk21.com)
# License: GPL
# last modified 03.2013

"""Simulates Total internal Reflection using the transfer matrix class"""

import numpy as N
import pyFresnelInit
import pyFresnel.transfer_matrix as TM
Layer=TM.Layer
import matplotlib.pyplot as P
pi=N.pi
c=299792458  #m/s - speed of light
mod2=lambda a : a*a.conj() #modulus squared

## Protected Al
#From Freesnell, a reproduction of http://www.kruschwitz.com/HR%27s.htm
lamda = N.linspace(.3e-6,.9e-6,200) # (m) wavelength
w = 2*pi*c/lamda # (Hz) frequency (natural)

#refractive indices.
interface = TM.Filter(
            [Layer(3.0,None),
            #TM.Layer(1.0+5j,None)],
            #TM.LayerUniaxial(1.0,1.0,None)],
            Layer(1.0,None)],
            w=w,
            pol='TM',
            theta=pi/4)

#
z = N.linspace(-0.05e-6,0.05e-6,2000)
zaxis = z*1e6 #(um)

    
Efields=interface.calculate_E(z=z,pol='TM')
    
Efields2=interface.calculate_E(z,pol='TE')
"""    
#check TM transmission coefficient
interface.pol='TE' #this is so we calculate the n2cos(theta2)/(n1cos(theta1)) factor (rather than the n1cos(theta2)/(n2cos(theta1))
print 'TM Transmission at %g um = ' %(lamda[fi]*1e6), interface._lambda((interface[0],interface[-1]))[fi]*(mod2(Efields['Ez'][0,fi])+mod2(Efields['Ex'][0,fi]))

#check TE transmission coefficient
print 'TE Transmission at %g um = ' %(lamda[fi]*1e6), interface._lambda((interface[0],interface[-1]))[fi]*mod2(Efields2['Ey'][0,fi])
"""    
#######
fi = 100 #choose index for frequency (this is equiv. to 5.5THz for this script).

ax1 = P.subplot(111)

#ax1.fill_between(zaxis,mod2(Efields['Ex']).min(axis=1),mod2(Efields['Ex']).max(axis=1),label="|Ex|**2")
#ax1.fill_between(zaxis,mod2(Efields['Ez']).min(axis=1),mod2(Efields['Ez']).max(axis=1),facecolor='green',label="|Ez|**2")
#ax1.fill_between(zaxis,mod2(Efields['Dz']).min(axis=1),mod2(Efields['Dz']).max(axis=1),facecolor='red',label="|Dz|**2")
#ax1.fill_between(zaxis,mod2(Efields2['Ey']).min(axis=1),mod2(Efields2['Ey']).max(axis=1),facecolor='yellow',label="|Ey|**2")

ax1.plot(zaxis,mod2(Efields['Ex'][:,fi]),label="|Ex|**2")
ax1.plot(zaxis,mod2(Efields['Ez'][:,fi]),label="|Ez|**2")
ax1.plot(zaxis,mod2(Efields['Dz'][:,fi]),label="|Dz|**2")
ax1.plot(zaxis,mod2(Efields2['Ey'][:,fi]),label="|Ey|**2")

ax1.set_xlabel("distance (um)")
ax1.set_ylabel("|E|**2")
ax1.legend()

ax1.set_ylim([0,6])
    
P.show()

