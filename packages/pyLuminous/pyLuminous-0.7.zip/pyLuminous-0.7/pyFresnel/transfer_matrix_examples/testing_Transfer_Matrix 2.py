"""Testing the Transfer matrix code for isotropic absorbing medium"""
import matplotlib.pyplot as pl
import numpy as N
import pyFresnelInit
import pyFresnel.fresnel as Fr
import pyFresnel.transfer_matrix as TM
pi=N.pi
c=299792458  #m/s - speed of light
    
f1=pl.figure(1)
ax1=f1.add_subplot(111)
f2=pl.figure(2)
ax2=f2.add_subplot(111)
    
theta=N.arange(0.0,90.0,0.2)
theta2=theta*pi/180.0
I=Fr.Interface(n1=1.0,n2=1.5,theta=theta2)
    
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
    
######### Code for Transfer Matrix Model of interface

TM0 = TM.Filter([TM.Layer(1.0,None),
                TM.Layer(1.5,None)],
                w=None,
                pol='TM',
                theta=theta2)

theta2,TM_r_p,TM_t_p = TM0.calculate_r_t()
theta2,TM_R_p,TM_T_p = TM0.calculate_R_T()
TM0.pol='TE'
theta2,TM_r_s,TM_t_s = TM0.calculate_r_t()
theta2,TM_R_s,TM_T_s = TM0.calculate_R_T()

ax1.plot(theta,TM_r_s,'--',label="TM r_s")
ax1.plot(theta,TM_r_p,'--',label="TM r_p")
ax1.plot(theta,TM_t_s,'--',label="TM t_s")
ax1.plot(theta,TM_t_p,'--',label="TM t_p")

ax2.plot(theta,TM_R_s,'--',label="TM R_s")
ax2.plot(theta,TM_R_p,'--',label="TM R_p")
ax2.plot(theta,TM_T_s,'--',label="TM T_s")
ax2.plot(theta,TM_T_p,'--',label="TM T_p")


#########
ax1.set_xlabel("Angle of Incidence (degrees)")
ax1.set_ylabel("Field Amplitudes")
ax2.set_xlabel("Angle of Incidence (degrees)")
ax1.set_ylabel("Transmittance/Reflectance")
ax1.legend()
ax2.legend()
pl.show()