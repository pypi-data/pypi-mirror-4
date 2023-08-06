"""Trying to replicate some graphs from Pettersson's 1999 paper "Modeling photocurrent
action spectra of photovoltaic devices based on organic thin films

"""

fig4 = True
fig5 = True
fig6 = True
fig7a= True
fig7 = True

import numpy as N
import matplotlib
import matplotlib.pyplot as P
import matplotlib.image as image

import pyFresnelInit
import pyFresnel.transfer_matrix as TM
import pyFresnel.incoherent_transfer_matrix as ITM
from scipy.interpolate import interp1d,splrep,splev
import pyFresnel.constants as C
c = C.c
pi = C.pi
from pyFresnel.transfer_matrix import LayerUniaxial,Layer
print "libraries imported"

#import pycallgraph
#import cProfile

## helper function for find axes in figure

def onclick(event):
    print 'button=%d, x=%d, y=%d, xdata=%f, ydata=%f'%(
        event.button, event.x, event.y, event.xdata, event.ydata)

## Create materials

def creatematerial(data):
    """takes an array of column data: 
    spectral axis, n, k
    and returns a function that spline interoplates over the
    refractive index data
    """    
    axis=data[:,0]
    #nk=data[:,1]+1j*data[:,2]
    #nkfunc = interp1d(axis,nk) #basic
    #nkfunc2 = interp1d(axis,nk,kind='cubic') # doesn't work.
    nkspline_real = splrep(axis,data[:,1],s=0)
    nkspline_imag = splrep(axis,data[:,2],s=0) #library doesn't work with complex numbers?
    return lambda axis: splev(axis,nkspline_real,der=0)+1j*splev(axis,nkspline_imag,der=0)

#Sopra data loader
def loadMAT(fname):
    with file(fname) as fobj:
        output=[]
        for line in fobj:
            linelist=line.split('*')
            if linelist[0]=='DATA1':
                output.append(map(float,linelist[2:5])) # data stored as wavelength(nm),n,k
        return N.array(output)

def createSOPRAmaterial(fname):
    """takes an array of column data: 
    spectral axis, n, k
    and returns a function that spline interoplates over the
    refractive index data
    """    
    data=loadMAT(fname) 
    axis=c*2*pi*1e9/data[:,0] #natural frequency from wavelength (nm)
    #nk=data[:,1]+1j*data[:,2]
    #nkfunc = interp1d(axis,nk) #basic
    #nkfunc2 = interp1d(axis,nk,kind='quadratic') # doesn't work.
    nkspline_real = splrep(axis[::-1],data[::-1,1],s=0)
    nkspline_imag = splrep(axis[::-1],data[::-1,2],s=0) #library doesn't work with complex numbers?
    return lambda axis: splev(axis,nkspline_real,der=0)+1j*splev(axis,nkspline_imag,der=0)

##PEOPT

class PEOPTLayer(Layer):
    def __init__(self,d,coh=True):
        """PEOPT refractive index data between 600 - 100nm wavelength"""
        data=N.loadtxt('Pettersson1999_data//Pettersson1999fig.4_n.csv',skiprows=1,delimiter=',')
        data[:,0]=c*2*pi*1e9/data[:,0] #convert from nm to w (natural Hz)
        self._nkspline_real = splrep(data[::-1,0],data[::-1,1],s=0) #need increasing w for spline procedure to work
        
        data2=N.loadtxt('Pettersson1999_data//Pettersson1999fig.4_k.csv',skiprows=1,delimiter=',')
        data2[:,0]=c*2*pi*1e9/data2[:,0] #convert from nm to w (natural Hz)
        self._nkspline_imag = splrep(data2[::-1,0],data2[::-1,1],s=0)        
        #self.n = lambda axis: splev(axis,self._nkspline_real,der=0)+1j*splev(axis,self._nkspline_imag,der=0)
        
        self.d = d
        self.coh=coh
        
    def n(self,w):
        return splev(w,self._nkspline_real,der=0)+1j*splev(w,self._nkspline_imag,der=0)

##

def makefig4():
    im=image.imread('.//Pettersson1999_data//Pettersson1999fig.4.png')
    
    fig4 = P.figure()
    fig4im = fig4.add_axes([0,0,1,1], frameon=False)
    fig4im.set_axis_off()
    fig4im.imshow(im)
    #cid = fig4.canvas.mpl_connect('button_press_event', onclick)
    overlay=(196,505.5,717,-469)
    fig4ax = fig4.add_axes((0.3,0.3,0.5,0.5),axisbg='none')
    fig4ax2 = fig4ax.twinx()
    def on_resize(event):
        #had to add FigureCanvasBase.resize_event(self) to the end of resize_event in backend_qt4.py for this to work.
        Bbox = matplotlib.transforms.Bbox.from_bounds(*overlay)
        trans = fig4im.transData + fig4.transFigure.inverted()
        rect = matplotlib.transforms.TransformedBbox(Bbox, trans).bounds
        fig4ax.set_position(rect)
        fig4ax2.set_position(rect)
    on_resize(None)
    cid2 = fig4.canvas.mpl_connect('resize_event', on_resize)
     
    wav = N.linspace(300,1000,400) #wavelength (nm)
    w = c/wav*1e9*2*pi
    PEOPTex=PEOPTLayer(0.0)
    fig4ax.plot(wav,PEOPTex.n(w).real,'b')
    fig4ax2.plot(wav,PEOPTex.n(w).imag,'r')
    
    fig4ax.set_xlim([280,1020])
    fig4ax.set_ylim([1.0,2.0])
    fig4ax2.set_ylim([0.0,0.3])

    #command = """P.show()"""
    #cProfile.runctx( command, globals(), locals(), filename="Matplotlibqt4Context2.profile" )
    
    #pycallgraph.start_trace()
    #P.show()
    #pycallgraph.make_dot_graph('test2.svg',format='svg')
    
    P.show()

if fig4: makefig4()
    
    
## C60

class C60Layer(Layer):
    def __init__(self,d,coh=True):
        """C20 refractive index data between 600-1000nm wavelength"""
        data=N.loadtxt('Pettersson1999_data//Pettersson1999fig.5_n.csv',skiprows=1,delimiter=',')
        data[:,0]=c*2*pi*1e9/data[:,0] #convert from nm to w (natural Hz)
        self._nkspline_real = splrep(data[::-1,0],data[::-1,1],s=0) #need increasing w for spline procedure to work
        
        data2=N.loadtxt('Pettersson1999_data//Pettersson1999fig.5_k2.csv',skiprows=1,delimiter=',')
        data2[:,0]=c*2*pi*1e9/data2[:,0] #convert from nm to w (natural Hz)
        self._nkspline_imag = splrep(data2[::-1,0],data2[::-1,1],s=0)        
        #self.n = lambda axis: splev(axis,self._nkspline_real,der=0)+1j*splev(axis,self._nkspline_imag,der=0)
        
        self.coh=coh
        self.d = d
        
    def n(self,w):
        return splev(w,self._nkspline_real,der=0)+1j*splev(w,self._nkspline_imag,der=0)

##

def makefig5():
    im=image.imread('.//Pettersson1999_data//Pettersson1999fig.5.png')
    
    fig = P.figure()
    figim = fig.add_axes([0,0,1,1], frameon=False)
    figim.set_axis_off()
    figim.imshow(im)
    #cid = fig.canvas.mpl_connect('button_press_event', onclick)
    overlay=(177,525.5,716,-471.5)
    figax = fig.add_axes((0.3,0.3,0.5,0.5),axisbg='none')
    figax2 = figax.twinx()
    def on_resize(event):
        #had to add FigureCanvasBase.resize_event(self) to the end of resize_event in backend_qt4.py for this to work.
        Bbox = matplotlib.transforms.Bbox.from_bounds(*overlay)
        trans = figim.transData + fig.transFigure.inverted()
        rect = matplotlib.transforms.TransformedBbox(Bbox, trans).bounds
        figax.set_position(rect)
        figax2.set_position(rect)
    on_resize(None)
    cid2 = fig.canvas.mpl_connect('resize_event', on_resize)
     
    wav = N.linspace(300,1000,400) #wavelength (nm)
    w = c/wav*1e9*2*pi
    C60ex=C60Layer(0.0)
    figax.plot(wav,C60ex.n(w).real,'b')
    figax2.plot(wav,C60ex.n(w).imag,'r')
    
    figax.set_xlim([280,1020])
    figax.set_ylim([1.0,2.6])
    figax2.set_ylim([0.0,1.0])

    P.show()

if fig5: makefig5()
    
## fig.6

def makefig6():
    im=image.imread('.//Pettersson1999_data//Pettersson1999fig.6.png')
    
    fig = P.figure()
    figim = fig.add_axes([0,0,1,1], frameon=False)
    figim.set_axis_off()
    figim.imshow(im)
    cid = fig.canvas.mpl_connect('button_press_event', onclick)
    overlay=(210,550.8,717,-472)
    figax = fig.add_axes((0.3,0.3,0.5,0.5),axisbg='none')
    def on_resize(event):
        #had to add FigureCanvasBase.resize_event(self) to the end of resize_event in backend_qt4.py for this to work.
        Bbox = matplotlib.transforms.Bbox.from_bounds(*overlay)
        trans = figim.transData + fig.transFigure.inverted()
        rect = matplotlib.transforms.TransformedBbox(Bbox, trans).bounds
        figax.set_position(rect)
    on_resize(None)
    cid2 = fig.canvas.mpl_connect('resize_event', on_resize)
     
    wav = N.linspace(300,1000,400) #wavelength (nm)
    w = c/wav*1e9*2*pi
    PEOPTex=PEOPTLayer(0.0)
    figax.plot(wav,PEOPTex.n(w).imag/wav*4*pi*1e7*1e-5,'b')
        
    C60ex=C60Layer(0.0)
    figax.plot(wav,C60ex.n(w).imag/wav*4*pi*1e7*1e-5,'r')
    
    figax.set_xlim([400,700])
    figax.set_ylim([0.0,1.0])
    
    P.show()

if fig6: makefig6()
    
## fig7. Thin Film

fig7wav = N.linspace(300,1000,400) #wavelength (nm)
fig7w = c/fig7wav*1e9*2*pi

from metals_nk import Al #refractive index of Al
glass = 1.5164
ITO = createSOPRAmaterial('ITO2.MAT')

class PEDOTLayer(Layer):
    def __init__(self,d,ratio=0.28,coh=True):
        """PEDOT refractive index data between 350-900nm wavelength
        ratio is the ratio of PEDOT:PSS (fraction of PEDOT)"""
        data=N.loadtxt('Pettersson1999_data//PEDOT-PSS-1-6-n.csv',skiprows=1,delimiter=',')
        data[:,0]=c*2*pi*1e9/data[:,0] #convert from nm to w (natural Hz)
        self._nspline_a= splrep(data[::-1,0],data[::-1,1],s=0) #need increasing w for spline procedure to work
        data=N.loadtxt('Pettersson1999_data//PEDOT-PSS-1-2.5-n.csv',skiprows=1,delimiter=',')
        data[:,0]=c*2*pi*1e9/data[:,0] #convert from nm to w (natural Hz)
        self._nspline_b = splrep(data[::-1,0],data[::-1,1],s=0) #need increasing w for spline procedure to work

        data2=N.loadtxt('Pettersson1999_data//PEDOT-PSS-1-6-k.csv',skiprows=1,delimiter=',')
        data2[:,0]=c*2*pi*1e9/data2[:,0] #convert from nm to w (natural Hz)
        self._kspline_a = splrep(data2[::-1,0],data2[::-1,1],s=0)
        data2=N.loadtxt('Pettersson1999_data//PEDOT-PSS-1-2.5-k.csv',skiprows=1,delimiter=',')
        data2[:,0]=c*2*pi*1e9/data2[:,0] #convert from nm to w (natural Hz)
        self._kspline_b = splrep(data2[::-1,0],data2[::-1,1],s=0)

        #self.n = lambda axis: splev(axis,self._nkspline_real,der=0)+1j*splev(axis,self._nkspline_imag,der=0)
        self.ratio = ratio
        
        self.d = d
        self.coh=coh
        
    def n(self,w):
        a= splev(w,self._nspline_a,der=0)+1j*splev(w,self._kspline_a,der=0)
        ratioa=1./7.0
        b= splev(w,self._nspline_b,der=0)+1j*splev(w,self._kspline_b,der=0)
        ratiob=1./3.5
        return a + (b - a)*(self.ratio - ratioa)/(ratiob - ratioa)

def makefig7a():
    fig = P.figure()
    figax=fig.add_subplot(111)
    figax2=figax.twinx()
    
    wav = N.linspace(350,900,400) #wavelength (nm)
    w = c/wav*1e9*2*pi
    PEDOT=PEDOTLayer(0.0)
    figax.plot(wav,PEDOT.n(w).real,'b')
    figax2.plot(wav,PEDOT.n(w).imag,'r')
    
    figax.set_xlim([280,1020])
    figax.set_ylim([1.0,2.6])
    
    figax.set_xlabel("wavelength (nm")
    figax.set_ylabel("refractive index")
    figax2.set_ylabel("k")

    P.show()

if fig7a: makefig7a()

fig7 = ITM.IncoherentFilter(
                [Layer(1.0,None),
                Layer(glass,1e-3,coh=False),
                Layer(ITO,120e-9),
                PEDOTLayer(110e-9,ratio=0.14),
                PEOPTLayer(40e-9),
                C60Layer(35e-9),
                Layer(Al,None)
                ],
                pol='TM',
                theta=0.0,
                w=fig7w)

def makefig7():
    im=image.imread('.//Pettersson1999_data//Pettersson1999fig.7.png')
    
    fig = P.figure()
    figim = fig.add_axes([0,0,1,1], frameon=False)
    figim.set_axis_off()
    figim.imshow(im)
    cid = fig.canvas.mpl_connect('button_press_event', onclick)
    
    overlay=(173.5,566.8,716.5,-514)
    figax = fig.add_axes((0.3,0.3,0.5,0.5),axisbg='none')
    def on_resize(event):
        #had to add FigureCanvasBase.resize_event(self) to the end of resize_event in backend_qt4.py for this to work.
        Bbox = matplotlib.transforms.Bbox.from_bounds(*overlay)
        trans = figim.transData + fig.transFigure.inverted()
        rect = matplotlib.transforms.TransformedBbox(Bbox, trans).bounds
        figax.set_position(rect)
    on_resize(None)
    cid2 = fig.canvas.mpl_connect('resize_event', on_resize)
        
    axis,R,T=fig7.calculate_R_T()
    
    figax.plot(fig7wav,R,'b')
    figax.plot(fig7wav,1-R,'r')
    
    figax.set_xlim([400,700])
    figax.set_ylim([0.0,1.0])
    
    P.show()

if fig7: makefig7()

