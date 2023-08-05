#! /usr/bin/env python
#===============================================================================
# processing.processbase
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

""" docstring """

import numpy as np

# low level functions
#---------------------
def _pk(data, p0=0.0, p1=0.0):
    """
    phase data
    p0 and p1 are in degrees
    """
    size = data.shape[-1]
    p0 = np.deg2rad(p0)
    p1 = np.deg2rad(p1)   
    phase = p0 + p1 * np.arange(float(size)) / float(size)
    return data * np.exp(1.0j * phase).astype(data.dtype)  

def _em(data, lb=0.0):
    """
    Exponential multiplication
    """
    return data * np.exp(-np.pi * np.arange(data.shape[-1]) * lb).astype(data.dtype)

def _zf(data, size):
    """
    zerofilling
    """
    shape = list(data.shape)
    shape[-1] = size-shape[-1]
    new = np.zeros(shape).astype(data.dtype)
    return np.hstack((data,new))

def _ft(data, si=None):
    """
    Fourier transform (first point is divided by two) and to get unity integrals the results of _ft is divided by si/2
    """
    if si is None: 
        si = data.shape[-1]
    data[0] = data[0]/2.
    return np.fft.fftshift(np.fft.fft(data, si, axis=-1), -1)/float(si/2)

def _ift(data, si=None):
    """
    Inverse fourier transform (inverse operation with respect to _ft)
    """
    if si is None: 
        si = data.shape[-1]
    ndata = np.fft.ifft(np.fft.ifftshift(data, -1), si, axis=-1)*float(si/2)
    ndata[0]=ndata[0]*2.
    return ndata

if __name__ == '__main__':
    
    pass