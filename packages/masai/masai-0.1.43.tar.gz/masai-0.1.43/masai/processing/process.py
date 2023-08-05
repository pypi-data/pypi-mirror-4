#! /usr/bin/env python
# -*- coding: utf-8 -*-
#===============================================================================
# processing.process
#===============================================================================
# Copyright (C) 2012-2013 Christian Fernandez
#       Laboratoire Catalyse et Spectrochimie, Caen, France.  
#       christian.fernandez@ensicaen.fr
# This software is governed by the CeCILL-B license under French law 
# and abiding by the rules of distribution of free software.  
# You can  use, modify and/ or redistribute the software under 
# the terms of the CeCILL-B license as circulated by CEA, CNRS and INRIA
# at the following URL "http://www.cecill.info".
# See Licence.txt in the main masai source directory
#===============================================================================
"""
.. _process:

This module contains the processing commands.

"""
import sys

#===============================================================================
# logger
#===============================================================================
import logging
logger = logging.getLogger()

import numpy as np

from scipy.optimize import optimize

from processbase import _em, _pk, _ft, _ift, _zf
 
# definitions

# MC2 or FnMODE table
undefined = -1
QF = 0
QSEQ = 1
TPPI = 2 
STATES = 3
STATESTPPI = 4
ECHOANTIECHO = 5

# save stdout
STDOUT = sys.stdout
# save stderr
STDERR = sys.stderr

__all__ = ['bc', 'tdeff','em', 'azf','zf', 'reducesampling', 'clipping', 'cursor2max', 'pk', 'apk',
           'ft', 'ift', 'efp', 'xf2', 'xf1', 'findregion', 'largest_power_of_2', 'transpose', 'makestates', 
           'shearing_ratio']
#===============================================================================
# Blackhole
#===============================================================================
class Blackhole: 
    """Utility class used to suppress some output
    """
    def write(self, *msg): 
        pass
    
#===============================================================================
# apodization, sampling and zerofilling
#===============================================================================
def bc(fd):
    """Correct fid offsets
    
    if BC_mod parameter is set, a baseline correction is applied to the fid
    in the direct (or indirect if transposed data) dimension. 
    The average value of the last quarter of the fid 
    is substracted to the whole data

    data ndarray are modified in place

    .. warning:: 
    
        fd.data should ideally be some time domain data, i.e., 
        is_freq set to false or wrong results can occurs
        
    .. todo:: 
    
        Only quad bc correction mode is setup: handle different mode of BC correction.   
    
    Parameters
    ----------
    fd : Source instance
        Contains bruker NMR parameters and data 
    

        
    Examples
    --------
        
        >>> from masai.api import *
        >>> fd = Source(path = 'test/1')
        >>> bc(fd)
        
        or for 2D
        
        >>> fd= Source(path='test/2')
        >>> bc(fd)

            
    """
    logger.debug("bc")
    size = fd.data.shape[-1]
    if fd.BC_mod > 0: 
        bc = np.mean(fd.data[..., -size / 4:], axis= -1)
        fd.data = np.transpose(np.transpose(fd.data) - bc)
     
    return

def tdeff(fd):
    """
    reduce the effective time domain size (td).
    
    """
    if fd.is_freq[-1]:
        return 

    logger.debug("tdeff")
    
    if fd.TDeffSAV[-1]>0.0 and (fd.TDeff[-1] > fd.TDeffSAV[-1] or fd.TDeff[-1] > fd.TD[-1]):
        logger.error("TDeff was not applied: it was already performed on a shorter size or it is geater than TD")
        return
    
    fd.data = fd.data[:fd.TDeff[-1]] 
    
    fd.TDeffSAV[-1] = fd.TDeff[-1]
    
    return

def em(fd, lb=None):
    """
    Exponential apodization
    
    The command em performs an exponential window multiplication of the fd. 
    It is the most used window function for NMR spectra. 
    em multiplies each data point :math:`k` with the factor:
    
    .. math::
        em(k) = \\exp\\left[ -\\pi  \\, \\frac{k \\, LB}{2 \\, SW\_h}\\right]
        
    where LB (the line broadening factor in Hz) is a processing parameter 
    and SW_h (the spectral width) an acquisition status parameter.
    
    
    Parameters
    ----------
    fd : Source instance
        Contains bruker NMR parameters and  data 
    lb : float, optional, None by default
        Line broadening in Hz, replace the value stored in fd if specified
    


    Examples
    --------
        
        >>> from masai.api import *
        >>> fd = Source(path = 'test/1')
        >>> em(fd)
        
        or for 2D
        
        >>> fd= Source(path='test/2')
        >>> em(fd)

    """
    if fd.is_freq[-1]:
        return
    
    sw = fd.SW_h[-1]
    if lb is not None: fd.LB[-1] = lb
    lb = fd.LB[-1]- fd.LBSAV[-1]  # Inverse exponential width
    
    if abs(lb)>0.0 : 
        logger.debug("em")
        fd.data = _em(fd.data, lb / sw / 2.) 
    
    fd.LBSAV[-1] = fd.LB[-1]
    
    return

def azf(fd):
    """ 
    Automatic zero filling to two times the next largest power of two
    
    Parameters
    ----------
    fd : Source instance
        Contains bruker NMR parameters and  data
    


    Examples
    --------
        
        >>> from masai.api import *
        >>> fd = Source(path = 'test/1')
        >>> azf(fd)
        
        or for 2D
        
        >>> fd= Source(path='test/2')
        >>> azf(fd)

    """
    logger.debug("azf")
    
    size = fd.data.shape[-1]
    size = largest_power_of_2(size)
    zf(fd, size * 2)
    
    return

def zf(fd, size):
    """ 
    zero filling to the specified size.
    
    Parameters
    ----------
    fd : Source instance
        Contains bruker NMR parameters and  data
    size : Int
        Desired new data size after zero filling
        

        
    Examples
    --------
        
        >>> from masai.api import *
        >>> fd = Source(path = 'test/1')
        >>> zf(fd, 2**14)
        
        or for 2D
        
        >>> fd= Source(path='test/2')
        >>> zf(fd, 2**14)


    """
    logger.debug("zf")
 
    fd.data = _zf(fd.data, size)
    
    return

def reducesampling(fd, sampling):
    """Divide the sampling rate by the sampling parameter
    
    Undersampling can be used to reduce the size of the spectral window, e.g,
    
    * if sampling=3, then data are taken every three points in the direct dimension, 
    * or if sampling=(3,2), then additionnaly, a double sampling is performed in the second dimension
    
    works always on the original data (suppressing previous apodization for instance). So it should be the first 
    action to perform on a fid.
    
    Parameters
    ----------
    fd : Source Instance
        Should be time domain data
    sampling : int or tuple of int 
        Divider to resample the fd.data ndarray
        The size of the Tuple should be fd.data.shape
        
    Examples
    --------
        
        >>> from masai.api import *
        >>> fd = Source(path = 'test/1')
        >>> reducesampling(fd, 6)
        
        or for 2D
        
        >>> fd= Source(path='test/2')
        >>> reducesampling(fd, 6)

    """
    if fd.is_freq[-1]:
        # this apply only to time domain data
        return
    logger.debug("reducesampling")
    
    if isinstance(sampling, tuple):
        sampling_2 = sampling[0]
        sampling_1 = sampling[1]
    else:
        sampling_2 = sampling
        sampling_1 = 1.0
        
    if sampling_2 > 0:
        fd.data = fd.data_orig[..., 0::1 * sampling_2]
        size = fd.data.shape[-1]
        fd.SW[-1] = fd.SW[-1] * size / fd.TD[-1]
        fd.SW_h[-1] = fd.SW_h[-1] * size / fd.TD[-1]
        fd.TD[-1] = size
        fd.is_resized = True
     
    #we need to set the position of the phcursor
    fd.phcursor = cursor2max(fd)
       
    if sampling_1 > 1:
        # warning here this strongly depends on the acquisition mode
        # fd.data = fd.data[0::1*sampling_2]
        logger.warn("Warning: reduce sampling in indirect dimension not done. Not yet implemented")
        return False

    return

def clipping(fd):
        """
        reduce the size of the transformed spectra to a smaller range (clipping region).
        The number of points is however made equal to a power of two.
        
        Parameters
        ----------
        fd : Source Instance
            Should be the frequency domain data
            clipping region is known from the clip attribute of fd
        
        """
        if not fd.is_freq[-1]:
            # this apply only to FT transformed data
            return
    
        if not fd.clip:
            return
        
        # we make a temporary copy of the source as we do not want refreshing during
        fd_ = fd.copy()
        
        logger.debug('clipping')
        uc = fd.units
        x = uc[-1].ppm_scale()
        xlim = uc[-1].ppm_limits()
        if list(xlim)==fd.clip:
            return
        clipped = findregion(x, fd.clip)
        
        if len(clipped)%2!=0:
            # make it even
            clipped.append(clipped[-1]+1)
        
        shape = list(fd_.data.shape)
        shape[-1] = len(clipped)
        newdata = fd_.data.take(clipped).flatten()
        fd_.data = newdata.reshape(shape)

        # correct scaling units
        xhigh, xlow = float(x[clipped[-1]]) , float(x[clipped[0]])
        fd.SW[-1] = xhigh - xlow 
        fd.SW_h[-1] = fd.SW[-1] * fd.SFO1[-1]
        sr = (xlow + fd.SW[-1] / 2.) * fd.SFO1[-1]
        fd.SF[-1] = fd.SFO1[-1] - sr * 1.e-6
                
        # make the spectrum number of point a power of two (necesary for further simulation using simpson for instance)
        fd_.data.imag = 0.0       # we use a hilbert transform to avoid problem with edge artifacts
        fd_.is_freq[-1]=False
        fd_.data = _ift(fd_.data)
        fd_.data = fd_.data[:len(fd_.data)/2]
        azf(fd_)
        fd_.data = _ft(fd_.data)
        # correct for some baseline while returning the data
        if fd_.ndims>1:
            #TODO : check this
            dataT = fd_.data.T 
            fd_.data = (dataT - (np.mean(dataT[0:100])+np.mean(dataT[-100:-1]))/2.).T
        else:
            fd_.data = fd_.data - (np.mean(fd_.data[0:100])+np.mean(fd_.data[-100:-1]))/2.


        fd_.is_freq[-1] = True
        
        # restore to the original data
        fd.data = fd_.data.copy()
        
        uc = fd.units
        logger.debug("new limits : %s", str(uc[-1].ppm_limits()))
        logger.debug("new number of point %d", fd_.data.shape[-1])

        fd.forceupdatemodel = True
        
        return
 
#===============================================================================
# phase
#===============================================================================
def cursor2max(fd):
    """
    Find and set phcursor the position of the ideal reference peak for the 1st order phasing
    i.e., the maximum peak position. In order to avoir problems dur to sometimes 
    distorsions at the edge of the spectrum (digital filter problems), the search 
    is limited to the central portion of the spectrum
    
    Parameters
    ----------
    fd : Source instance
        Source instance 
        
    """
    if not fd.is_freq[-1]:
        # this search is not relevant for FID's
        return 0 
    
    s = list(fd.data.shape)
    si = s[-1]
    s[-1] = si/2 # we will work only on the half center
    lb = si/4.
    ub = 3.*lb
    data = fd.data[...,lb:ub]   #TODO: may be nicer to work with numpy masked array
    data = np.abs(data)
    cursor = np.argmax(data)  # this should give a flattened index on multidimensionnal array
    cursor = np.unravel_index(cursor, s)[-1] # so we unravel the indexes
    #set the fd attributes
    fd.phcursor = cursor + si/4. # do not forget that the indexwas found from the si/4 position

        
def pk(fd, p0=0, p1=0):
    """
    linear phase correction, work always on the last axis (axis=-1)
    If other axis need to be phased, first transpose the array
    The 1st order correction is calculated with respect to the 
    phcursor position (automatically set to the position of the 
    maximum peak intensity.
    
    Parameters
    ----------
    fd : Source instance
        Source instance 
    p0 : float, optional
        zero order phase correction, added to the value stored in fd
    p1 : float, optional
        1st order phase correction, added to the value stored in fd

    Examples
    --------
        
        >>> from masai.api import *
        >>> fd = Source(path = 'test/1')
        >>> ft(fd)
        >>> pk(fd)
        
        or for 2D
        
        >>> fd= Source(path = 'test/2')
        >>> ft(fd)
        >>> pk(fd)

   
    """ 
    if not fd.is_freq[-1]:
        # this apply only to fourier transformed data
        return  
    
    logger.debug("pk")
    if p0!=0 :  fd.PHC0[-1] = p0 + fd.PHC0[-1]
    if p1!=0 :  fd.PHC1[-1] = p1 + fd.PHC1[-1]
    
    p0 = fd.PHC0[-1] - fd.PHC0SAV[-1] 
    p1 = fd.PHC1[-1] - fd.PHC1SAV[-1] 
    if p0==0.0 and p1==0.0:
        return

    fd.data = _pk(fd.data, p0, p1)
    
    fd.PHC0SAV[-1] = fd.PHC0[-1]
    fd.PHC1SAV[-1] = fd.PHC1[-1]
        
    return

def apk(fd, delta=2.0):
    """ 
    Automatic linear phase correction (zero order phase only)

    .. todo:: 
    
        improve the choice of the processing area (parameter delta to change)
        
    Parameters
    ----------
    fd : Source instance
        Source instance 
    delta : float, optional, default=2
        Fraction of the maximum intensity to determine the optimization region 
            


    Examples
    --------
        
        >>> from masai.api import *
        >>> fd = Source(path = 'test/1')
        >>> ft(fd)
        >>> res = apk(fd)
        
        or for 2D
        
        >>> fd= Source(path='test/2')
        >>> ft(fd)
        >>> res2 = apk(fd)

    """
    if not fd.is_freq[-1]:
        # this apply only to FT transformed data
        return
    
    logger.debug("apk")
    # error function
    def phascalc(p, s, intervalle): 
        p0 = p[0]
        sc = s.copy()
        scp = _pk(sc, p0)[intervalle]
        return  np.arctan(np.sum(scp.imag) / np.sum(scp.real)) ** 2 # / np.sum(np.abs(sc.real) ** 2)

    pk(fd)
    
    n = fd.data.size / 4
    pwr = np.abs(fd.data)
    mi = np.unravel_index(np.argmax(pwr), fd.data.shape)[-1]
    s = fd.data[mi - n / 2:mi + n / 2]
    pwr = pwr[mi - n / 2:mi + n / 2]
    
    m = np.max(pwr)
    intervalle = pwr > (m / delta) 
        
    p0 = np.rad2deg(np.arctan(np.sum(s.imag) / np.sum(s.real)))
    p = (p0,)
    
    sys.stdout = Blackhole() #suppress output of the fmin function
    p0 = optimize.fmin(phascalc, p, args=(s, intervalle), xtol=1e-8)[0]
    sys.stdout = STDOUT # Restore normal output
    
    fd.PHC0[-1] = (fd.PHC0[-1]+p0) % 360.
    pk(fd)

    pmax = np.argmax(np.abs(fd.data.real))
    # pmax is found on a flattened array
    # so we use flatten() in the next line
    if fd.data.real.flatten()[pmax] < 0:   
        fd.PHC0[-1] = (fd.PHC0[-1]+180.) % 360.    
        pk(fd)
    
    logger.info("Automatic calculated phase was %.3f"%p0)
        
    return

def ft(fd):
    """
    Achieve the fourier transform (data should not be already transformed) 
    
    Note that an automatic zerofilling to the nearest power of two is automatically applied
    
    Parameters
    ----------
    fd : Source instance
        Contains bruker NMR parameters and  data

    Examples
    --------
        
        >>> from masai.api import *
        >>> fd = Source(path = 'test/1')
        >>> ft(fd)
        >>> ft(fd)
        False
        
        or for 2D
        
        >>> fd= Source(path='test/2')
        >>> ft(fd)

    """
    logger.debug("ft")
    
    if fd.is_freq[-1]:
        logger.warn("Data already transformed: use 'ift' instead?")
        return False
    
    # Zero filling
    si = fd.SI[-1] 
    zf(fd, si)
        
    # process ft
    fd.data = _ft(fd.data, si)
    fd.is_freq[-1] = True
    
    #we need to reset the position of the phcursor
    cursor2max(fd)
    
    return

def ift(fd):
    """
    Achieve the inverse fourier transform (data should be already transformed) 
    
    Note that an automatic zerofilling to the nearest power of two is automatically applied
    
    Parameters
    ----------
    fd : Source instance
        Contains bruker NMR parameters and  data
    


    Examples
    --------
        
        >>> from masai.api import *
        >>> fd = Source(path = 'test/1')
        >>> ft(fd)
        >>> ift(fd)
        
        or for 2D
        
        >>> fd= Source(path='test/2')
        >>> ft(fd)
        >>> ift(fd)

    """
    logger.debug("ift")
     
    if not fd.is_freq[-1]:
        logger.warn("Data not yet transformed: use 'ft' instead?")
        return False
    
    # process ft
    fd.data = _ift(fd.data)
    fd.data[fd.data.shape[-1]/2:] = 0.0
    fd.is_freq[-1] = False
    
    return

def efp(fd, autophase=False, delta=20):
    """
    Process sequential em, ft, pk bruker-like commands

    Parameters
    ----------
    fd : Source instance
        Contains bruker NMR parameters and  data
    autophase : bool, optional, default = False
        True if apk is applied instead of pk for automatic
        phasing
    delta : float, optional, default=20 
        (see apk function description for more information)  

    Examples
    --------
        
        >>> from masai.api import *
        >>> fd = Source(path = 'test/1')
        >>> efp(fd)
        
        or for 2D
        
        >>> fd= Source(path='test/2')
        >>> efp(fd)
        >>> efp(fd)
        False
        
    """
    logger.debug("efp")
    
    if fd.is_transposed:
        logger.warn("Data are transposed, we cannot use this procedure.")
        return False
    
    if fd.is_freq[-1]:
        logger.warn("The data are already transformed along F2")
        return False
    
    tdeff(fd) 
    em(fd) 
    ft(fd)
    
    if not autophase:
        pk(fd)
    else:
        apk(fd, delta)
    
    return
    
def xf2(fd, autophase=False, delta=20):
    """
    Process sequential em, ft, pk bruker-like commands (alias for efp, more specific for 2D spectra)

    
    Parameters
    ----------
    fd : Source instance
        Contains bruker NMR parameters and  data
    autophase : bool, optional, default = False
        True if apk is applied instead of pk for automatic
        phasing
    delta : float, optional, default=20 
        (see apk function description for more information)
        

    Examples
    --------
        
        >>> from masai.api import *
        >>> fd = Source(path = 'test/1')
        >>> xf2(fd)
        
        or for 2D
        
        >>> fd= Source(path='test/2')
        >>> xf2(fd)
   
    """     

    logger.debug("xf2:...")
    if fd.is_transposed: 
        logger.warn("the data are transposed, we cannot use this procedure (which apply only to indirect dimension")
        return False
    
    return efp(fd, autophase = autophase, delta = delta)

def xf1(fd, autophase=False, delta=20., filling=0,  shear=0.0, shift=0.0):
    """
    Fourier transform of the indirect dimension of a 2D NMR spectra

    Parameters
    ----------
    fd : Source instance
        Contains bruker NMR parameters and data
    autophase : bool, optional, default = False
        True if apk is applied instead of pk for automatic
        phasing
    delta : float, optional, default=20
        (see apk function description for more information)
    shear : Float, optional, default=0.0                
        If shear has a non-zero float value, it gives the shearing ratio to use
    shift: Float
        Amount of shifting in the F1 dimension in Hz
        


    Examples
    --------
        
        It is not possible for a 1D spectrum:
        
        >>> from masai.api import *
        >>> fd = Source(path = 'test/1')
        >>> xf2(fd)
        >>> xf1(fd)
        False
        
        For 2D:
        
        >>> fd= Source(path='test/2')
        >>> xf2(fd)
        >>> xf1(fd)
        >>> 
   
    """
    logger.debug("xf1:...")
    if fd.is_transposed:
        logger.warn('This procedure work only on non-transposed data.')
        return False
    
     
    if fd.PULPROG[-1].find('Multiplex') != -1 and fd.PARMODE[-1] == 1:
        # this is a specific case where the data where originally
        # acquired in 3D mode and processed with the MSM program
        # to give a 2D spectrum. In this case (this has to be changed in the MSM
        # processing, FnMODE and MC2 are wrong.
        # The mode of acquisition is in principle STATES, so we change it here
        fd.FnMODE[-1] = undefined
        fd.MC2[-1] = STATES
        
    mode = fd.FnMODE[-1]
    if mode == undefined:
        mode = fd.MC2[-1]
        
    if mode == STATES:  
        makestates(fd)
        
    else:
        # not yet implemented
        logger.warn("NotImplementedError")
        return False
    
    # phase for shearing and shift in F1
    if shear!=0.0 or shift!=0.0:
        logger.debug("shearing with ratio:%.5f"%shear)
        sw = fd.SW_h[0]  # remember that the table is transposed (direct dimension is now 0).
        si = fd.data.shape[0]
        in0 = fd.IN[0][0]
        p1 = -2.*3.14159*shear*sw*in0/si
        
        # additional F1 shift ?
        p0= -2.*3.14159*shift*in0;
        
        # create a 2D array of phases and performs the phase correction
        phases= np.fromfunction(lambda i0, i1: np.exp((p1*(i0-si/2)+p0)*i1*1.0j), fd.data.shape, dtype=float)
        fd.data = fd.data*phases
        
#    if ( mq<0 ) ph1= -ph1;
#    d1= fabs(ratio - (double)mq);
#    sfo11= d1*sfo1;

    if filling>0:
        zf(fd, filling)
         
    ft(fd)
    
    if not autophase:
        pk(fd)
    else:
        apk(fd, delta)
            
    #transpose back
    fd = transpose(fd)
    
    return

#===============================================================================
# utility functions
#===============================================================================
def findregion(xdata, region):
    """Return an array of indice corresponding to a given region
    
    xdata: ndarray
        array of abscisses (or ordinates) where to select a region
    region: list of float
        (low, high) list in any order giving the bound of the region 
    """
    _low = min(region)
    _high = max(region)
    region = np.argwhere((xdata <= _high) & (xdata >= _low)).ravel() 
    return list(region)
    
def largest_power_of_2(value):
    """
    Find the largest and nearest power of two of a value
    
    Parameters
    ----------
    value: int
    
    Returns
    -------
    pw: int
        Power of 2. 
        
    Examples
    --------
    
        >>> largest_power_of_2(1020)
        1024
        >>> largest_power_of_2(1025)
        2048
        >>> largest_power_of_2(0)
        2
        >>> largest_power_of_2(1)
        2
        
        
    """
    value = max(2, value)
    p = int(pow(2, np.ceil(np.log(value) / np.log(2))))
    return p

def transpose(fd):
    """Transpose 
    
    Parameters
    ----------
    fd : Source instance
        Contains bruker NMR parameters and data
    
    """
    if fd.ndims <2: 
        return False
    fd.is_transposed = not fd.is_transposed
    fd.data = np.transpose(fd.data)
    return

def makestates(fd):
    """Transforms according to the States procedure. 
    The data are transposed.
    
    Parameters
    ----------
    fd : Source instance
        Contains bruker NMR parameters and data
    
    """

    fd.is_transposed = True
    ar = np.transpose(fd.data[::2]) # transposed real part 
    ai = np.transpose(fd.data[1::2]) # transposed imag part
    fd.data = ar.real + ai.real * 1.0j
    return

def shearing_ratio(fd, p=3, q=0):
    """
    Calculation of the MQMAS or STMAS experiments shearing ratio
    
    For MQMAS, the shearing ratio is 
    
    .. math:: 
        k =\\frac{1}{9} \\frac{p \\left( -17{{p}^{2}}+36 I(I+1)-10 \\right)}{4 I( I+1)-3}
    
    For STMAS, the shearing ratio is
    
    .. math::
        k=\\frac{17}{3}\\frac{q^2}{\\left( 4I\\left( I+1 \\right)-3 \\right)}-1
    
    Examples
    --------
    
        >>> from masai.api import Source, shearing_ratio
        >>> f = Source(path='test/1')
        >>> shearing_ratio(f)
        1.5833333333333333
        >>> shearing_ratio(f, 5)
        2.0833333333333335
        
        
    Parameters
    ----------
    fd : Source instance
        Contains the required parameters
    p : Int, optional 
        default = 3 (3Q)
        multi-quantum order of the selected coherence (if mq==1 and q!=0 then a STMAS experiment is assumed, 
        if mq==2 then a STMAS Double_Quantum experiment is assumed instead. In all other case (where odd mq>2) 
        then MQMAS experiment is assumed. 
    q : Int, optional
        satelitte order for STMAS.
                
    returns
    -------
    k : float
        Ratio corresponding to the MQMAS shearing
        
    """

    I = fd.NUC1[-1].spin
    nspin = int(np.ceil(2.0 * I))
    p = float(abs(p))    
    q = float(q)
    
    if p == nspin:
        p = -p
    
    if p > nspin:
        logger.warn('coherence order p cannot be greater than 2*I')
        return 0
    
    if p > 2 or p == -nspin: 
        # MQMAS experiment assumed
        ratio = (p / 9.0) * (-17.0 * (p ** 2) + 36.0 * I * (I + 1.) - 10.0) / (4.0 * I * (I + 1.0) - 3.0)
        
    elif p == 1 and q != 0:
        # STMAS experiment assumed
        ratio = -((17.0 / 3.0) * (q ** 2) / (4.0 * I * (I + 1.0) - 3.0) - 1.0)
        
    return ratio
    