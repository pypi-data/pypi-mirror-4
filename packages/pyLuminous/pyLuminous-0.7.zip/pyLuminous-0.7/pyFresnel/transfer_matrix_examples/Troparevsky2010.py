"""Replicating the examples given in the 2010 paper by Troparevsky 
"Transfer-matrix formulism for the calculation of optical response in multilayers"
However, I believe that her formulism ignores the obliqueness factor of the
transmission coefficient although since his examples are for normal incidence this
might not matter so much.
I have also found a factor of 1.5 between her values of beta and my values in order
to replicate the results. Although beta=pi works as expected so maybe the relationship
is beta = pi*sin(coh/2)

I can't get figure 4 to work very well. Not even the coherent case and the partially
coherent layers don't seem to work in the same way either."""

import numpy as N
import matplotlib
import matplotlib.pyplot as P
import matplotlib.image as image

import pyFresnelInit
import pyFresnel.transfer_matrix as TM
import pyFresnel.incoherent_transfer_matrix as ITM
import pyFresnel.layer_types as layer_types
#from scipy.interpolate import interp1d,splrep,splev
import pyFresnel.constants as C
c = C.c
pi = C.pi
from pyFresnel.transfer_matrix import Layer
print "libraries imported"

#layer_types.SopraLayer.directory='.//Troparevsky2010_data' #only look for sopra data files in current directory

## Fig 2.

def makefig2():
    ##Load original image
    fig2 = P.figure()
    im=image.imread('.//Troparevsky2010_data//fig2.png')
    fig2im = fig2.add_axes([0,0,1,1], frameon=False)
    fig2im.set_axis_off()
    fig2im.imshow(im)
    overlay=(39,272,264,-264)
    fig2ax = fig2.add_axes((0.3,0.3,0.5,0.5),axisbg='none')
    def on_resize(event):
        #had to add FigureCanvasBase.resize_event(self) to the end of resize_event in backend_qt4.py for this to work.
        Bbox = matplotlib.transforms.Bbox.from_bounds(*overlay)
        trans = fig2im.transData + fig2.transFigure.inverted()
        rect = matplotlib.transforms.TransformedBbox(Bbox, trans).bounds
        fig2ax.set_position(rect)
    on_resize(None)
    cid2 = fig2.canvas.mpl_connect('resize_event', on_resize)
    
    #######
    
    lamda = N.linspace(0.2,1.2,500) # (um) wavelength
    w = 2*pi*c/lamda*1e6 # (Hz) frequency (natural)

    Sifilm = TM.Filter(
                [Layer(1.0,None),
                layer_types.SopraLayer('SICR',150e-9),
                Layer(1.0,None)],
                w=w,
                pol='TM',
                theta=0.0)
    
    w,R,T=Sifilm.calculate_R_T()
    #w,R2,T2=anti.calculate_R_T(pol='TE')
        
    fig2ax.plot(lamda,T,label="Transmission")
    
    #incoherent
    incoh_Sifilm = ITM.IncoherentFilter(
                [Layer(1.0,None),
                layer_types.SopraLayer('SICR',150e-9,coh=False),
                Layer(1.0,None)],
                w=w,
                pol='TM',
                theta=0.0)
                
    w,R2,T2=incoh_Sifilm.calculate_R_T()
    #w,R2,T2=anti.calculate_R_T(pol='TE')
        
    fig2ax.plot(lamda,T2,label="incoherent Transmission")
    
    #partially incoherent
    incoh_Sifilm2 = TM.Filter(
                [Layer(1.0,None),
                layer_types.SopraLayer('SICR',150e-9,coh=pi),
                Layer(1.0,None)],
                w=w,
                pol='TM',
                theta=0.0)
                
    #w,R3,T3=incoh_Sifilm.calculate_R_T()[2]
    T3 = N.mean([incoh_Sifilm2.calculate_R_T()[2] for _ in range(1000)],axis=0)
    print T3.shape
        
    fig2ax.plot(lamda,T3,label="incoherent Transmission")
    
    #fig2ax1.set_xlabel("Wavelength (m)")
    #fig2ax1.set_ylabel("Transmission")
    #fig2ax1.set_title("Fig2: Si Film")
    #ax1.legend()
    fig2ax.set_xlim([0.2,1.2])
    fig2ax.set_ylim([0.0,1.0])

## Fig 3.

def makefig3():
    ##Load original image
    fig3 = P.figure()
    im=image.imread('.//Troparevsky2010_data//fig3.png')
    fig3im = fig3.add_axes([0,0,1,1], frameon=False)
    fig3im.set_axis_off()
    fig3im.imshow(im)
    overlay=(44,316,306,-306)
    fig3ax = fig3.add_axes((0.3,0.3,0.5,0.5),axisbg='none')
    def on_resize(event):
        #had to add FigureCanvasBase.resize_event(self) to the end of resize_event in backend_qt4.py for this to work.
        Bbox = matplotlib.transforms.Bbox.from_bounds(*overlay)
        trans = fig3im.transData + fig3.transFigure.inverted()
        rect = matplotlib.transforms.TransformedBbox(Bbox, trans).bounds
        fig3ax.set_position(rect)
    on_resize(None)
    cid2 = fig3.canvas.mpl_connect('resize_event', on_resize)
    
    #######
    
    lamda = N.linspace(0.25,1.15,400) # (um) wavelength
    w = 2*pi*c/lamda*1e6 # (Hz) frequency (natural)

    Sifilm = TM.Filter(
                [Layer(1.0,None),
                layer_types.SopraLayer('SICR',150e-9),
                Layer(1.0,None)],
                w=w,
                pol='TM',
                theta=0.0)
    
    w,R,T=Sifilm.calculate_R_T()
    #w,R2,T2=anti.calculate_R_T(pol='TE')
        
    fig3ax.plot(lamda,T,label="Transmission")
    
    #incoherent
    incoh_Sifilm = ITM.IncoherentFilter(
                [Layer(1.0,None),
                layer_types.SopraLayer('SICR',150e-9,coh=False),
                Layer(1.0,None)],
                w=w,
                pol='TM',
                theta=0.0)
                
    w,R2,T2=incoh_Sifilm.calculate_R_T()
    #w,R2,T2=anti.calculate_R_T(pol='TE')
        
    fig3ax.plot(lamda,T2,label="incoherent Transmission")
    
    #partially incoherent
    incoh_Sifilm2 = TM.Filter(
                [Layer(1.0,None),
                layer_types.SopraLayer('SICR',150e-9,coh=pi),
                Layer(1.0,None)],
                w=w,
                pol='TM',
                theta=0.0)
    
    average=500
    #w,R3,T3=incoh_Sifilm.calculate_R_T()[2]
    T3 = N.mean([incoh_Sifilm2.calculate_R_T()[2] for _ in range(average)],axis=0)
    fig3ax.plot(lamda,T3,label="incoherent Transmission2")
    #beta = pi /3
    incoh_Sifilm2[1].coh=1.5*pi/3 #pi*N.sin(pi/3./2.)
    T3 = N.mean([incoh_Sifilm2.calculate_R_T()[2] for _ in range(average)],axis=0)
    fig3ax.plot(lamda,T3,label="incoherent Transmission2")    
    #beta = pi /4
    incoh_Sifilm2[1].coh=1.5*pi/4 #pi*N.sin(pi/4./2.)
    T3 = N.mean([incoh_Sifilm2.calculate_R_T()[2] for _ in range(average)],axis=0)
    fig3ax.plot(lamda,T3,label="incoherent Transmission2")
        
    #fig3ax.set_xlabel("Wavelength (m)")
    #fig3ax.set_ylabel("Transmission")
    #fig3ax.set_title("Fig2: Si Film")
    #ax1.legend()
    fig3ax.set_xlim([0.25,1.15])
    fig3ax.set_ylim([0.05,1.0])



## Fig 4.


class ZnOLayer(Layer):
    def __init__(self,d,coh=True):
        self.d = d # thickness of the layer (m)
        self.coh = coh # is layer coherent or incoherent, could also be a number between 0 and pi to decribe a partially coherent layer

    def n(self,w):     
        x =2*pi*c/w*1e6 # wavelength (um)
        #ZnO refractive index between 0.5 and 4um wavelength (refractiveindex.info)
        n = N.sqrt( 2.81418 + 0.87968*x**2/(x**2-0.3042**2) - 0.00711*x**2 ) 
        return n + 0j
    
    def __repr__(self):
        return "Layer"+"( ZnO,"+repr(self.d)+", coh="+repr(self.coh)+" )"

def makefig4():
    ##Load original image
    fig4 = P.figure()
    im=image.imread('.//Troparevsky2010_data//fig4.png')
    fig4im = fig4.add_axes([0,0,1,1], frameon=False)
    fig4im.set_axis_off()
    fig4im.imshow(im)
    overlay=(55,329,315,-319)
    fig4ax = fig4.add_axes((0.3,0.3,0.5,0.5),axisbg='none')
    def on_resize(event):
        #had to add FigureCanvasBase.resize_event(self) to the end of resize_event in backend_qt4.py for this to work.
        Bbox = matplotlib.transforms.Bbox.from_bounds(*overlay)
        trans = fig4im.transData + fig4.transFigure.inverted()
        rect = matplotlib.transforms.TransformedBbox(Bbox, trans).bounds
        fig4ax.set_position(rect)
    on_resize(None)
    cid2 = fig4.canvas.mpl_connect('resize_event', on_resize)
    
    #######
    
    lamda = N.linspace(0.2,1.4,400) # (um) wavelength
    w = 2*pi*c/lamda*1e6 # (Hz) frequency (natural)
    
    ZnOSifilm = TM.Filter(
                [Layer(1.0,None),
                ZnOLayer(150e-9),
                layer_types.SopraLayer('SICR',150e-9),
                Layer(1.0,None)],
                w=w,
                pol='TM',
                theta=0.0)
    
    w,R,T=ZnOSifilm.calculate_R_T()
    #w,R2,T2=anti.calculate_R_T(pol='TE')
        
    fig4ax.plot(lamda,T,label="Transmission")
    
    #incoherent
    incoh_ZnOSifilm = ITM.IncoherentFilter(
                [Layer(1.0,None),
                ZnOLayer(150e-9,coh=False),
                layer_types.SopraLayer('SICR',150e-9,coh=False),
                Layer(1.0,None)],
                w=w,
                pol='TM',
                theta=0.0)
                
    w,R2,T2=incoh_ZnOSifilm.calculate_R_T()
    #w,R2,T2=anti.calculate_R_T(pol='TE')
        
    fig4ax.plot(lamda,T2,label="incoherent Transmission")
    
    #partially incoherent
    incoh_ZnOSifilm2 = TM.Filter(
                [Layer(1.0,None),
                ZnOLayer(150e-9,coh=pi),
                layer_types.SopraLayer('SICR',150e-9,coh=pi),
                Layer(1.0,None)],
                w=w,
                pol='TM',
                theta=0.0)
    
    average=400
    #w,R3,T3=incoh_ZnOSifilm.calculate_R_T()[2]
    T3 = N.mean([incoh_ZnOSifilm2.calculate_R_T()[2] for _ in range(average)],axis=0)
    fig4ax.plot(lamda,T3,label="incoherent Transmission2")
    #Making ZnO layer coherent
    incoh_ZnOSifilm2[1].coh=True
    T3 = N.mean([incoh_ZnOSifilm2.calculate_R_T()[2] for _ in range(average)],axis=0)
    fig4ax.plot(lamda,T3,label="incoherent Transmission3")    
    #Changing Si layer's incoherence
    incoh_ZnOSifilm2[2].coh=pi/2#*N.sin(pi/2./2.)
    T3 = N.mean([incoh_ZnOSifilm2.calculate_R_T()[2] for _ in range(average)],axis=0)
    fig4ax.plot(lamda,T3,label="incoherent Transmission4")
        
    #fig4ax.set_xlabel("Wavelength (m)")
    #fig4ax.set_ylabel("Transmission")
    #fig4ax.set_title("Fig2: Si Film")
    #ax1.legend()
    fig4ax.set_xlim([0.0,1.4])
    fig4ax.set_ylim([0.0,1.0])








makefig2()
makefig3()
#makefig4()

P.show()
