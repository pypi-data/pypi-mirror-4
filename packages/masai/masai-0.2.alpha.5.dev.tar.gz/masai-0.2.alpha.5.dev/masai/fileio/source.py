#! /usr/bin/env python
# -*- coding: utf-8 -*-
#===============================================================================
# fileio.source
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
.. _source:

This module consist mainly in defining the class :class:`Source` which will contains
all data and parameters about the NMR experiments and the class 'ConvertUnits'.

It can be imported in a program as:

    >>> from masai.api import Source

"""

#===============================================================================
# Standard library imports.
#===============================================================================
import os
import string
import wx
from copy import deepcopy

#===============================================================================
# logger
#===============================================================================
import logging
logger = logging.getLogger()

#===============================================================================
# Enthought imports.
#===============================================================================
from traits.api import (HasTraits, Dict, Any, Directory, Bool, Property, Str,
                         Enum, Float, Array, on_trait_change, Instance, List,
                         cached_property, Either)
from traitsui.api import (Item, View, Action, Handler, Group)
from apptools.preferences.api import Preferences

#===============================================================================
# Numpy 
#===============================================================================
import numpy as np

#===============================================================================
# Local imports
#===============================================================================
from masai.processing.processbase import _ft, _ift
from masai.fileio.nmrglue.bruker import read, read_lowmem
from masai.database.isotopes import Isotopes
from masai.options import set_option, get_option, acqu_required, proc_required

# module global definition
status = {0:[''], 1:['', '2'], 2:['', '2', '3']}  
# give X which is used to read the proper acquXs, procXs files 
# according the parmode

#===============================================================================
# _OpenHandler (private class)
#===============================================================================
class _OpenHandler(Handler):
    """ The handler for the open dialog
    (should not be called directly by end-users)
    """
    def close(self, info, is_OK):        
        info.object._is_ok = is_OK
        return True

#===============================================================================
# Base class of a source
#===============================================================================
class Source(HasTraits):
    """This class handles a Bruker NMR source of data

    It first reads Bruker binary (ser/fid) files, Bruker JCAMP-DX parameter 
    (acqus) files, and Bruker pulse program (pulseprogram) files. The object created 
    is the main 'model' (in the MVC concept) of the **Masaï** application. 

    Examples
    --------

    We will use a wild import here for masai and use pylab librairies

    >>> from masai.api import *
    >>> import pylab as pl

    To create a new instance of a Source

    >>> fd1 = Source(path = 'test/1') 

    Plotting the datas (using the Source.data attribute)       

    1D case:

    >>> fig1 = pl.figure(1)  
    >>> p = pl.plot(fd1.data.real) 

    or 2D case:

    >>> fd2= Source(path='test/2') 
    >>> fig2 = pl.figure(2)
    >>> c = pl.contour(fd2.data.real, 30) 
    >>> pl.xlim(0,1024)
    (0, 1024)
    >>> pl.ylim(0,100)
    (0, 100)

    To print nmr parameters extracted from brukers acqu's and proc's

    >>> sf1, sf2 = fd2.SFO1
    >>> sf2 # is the SFO1 in direct dimension
    104.31847052

    Do not forget to add this:

    >>> pl.show()

    to be able to see the matplotlib plots.

    See :ref:`apihowto` for more examples. 

    Parameters
    ----------
    
    path : string, optional
        Default is None, so that a dialog ui will be launched.
        if path='last', then the last opened NMR file will be opened.
        if path is defined as a valid (existing) Bruker NMR directory:
        i.e., such as '/user/nmr/name_of_experiment/expno' 
        then the file will be opened without any further dialog.

    Attributes
    ----------
    
    data : numpy ndarray
        Contains the ndarray representing the current state of the source data
    data_orig: numpy ndarray
        Contains the ndarray representing the source data 
        (before any transforms)

    Notes
    -----
    
    Preferences are updated, so that next call to this class should point
    on the last used NMR path.

    """    
    #===========================================================================
    # data and model
    #===========================================================================
    # The directory to read source from
    _directory = Directory('', allow_none=False)

    # check if the specified file is valid
    _is_valid = Property(Bool(False), depends_on='_directory')

    # the message to display when errors in the file open dialog
    _message = Property(Str, depends_on='_directory')
    
    # data input (as read by the __init__ function): Read only
    data_orig = Property(Either(Array, Instance('masai.fileio.nmrglue.bruker.bruker_nd')))
    _data_orig = Either(Array, Instance('masai.fileio.nmrglue.bruker.bruker_nd'))
    xorig = Array
    norm = Float(1.)
    
    # data output (can be modified): original data are stored in data_orig
    # attributes for the view plot are specified as named arguments
    data = Property(Array)
    _data = Array

    #ndims
    ndims = Property(depends_on='_data_orig')

    # is-it processing running?
    is_processing = Bool(False)
    
    # is_transposed (required for processing multidimensionnal spectra)
    is_transposed = Bool(False)

    # is_freq say if the spectrum is fourier transformed 
    # or not in the various axis
    is_freq = List(Bool)

    # This flag is used mainly by the clipping ptrocedure
    is_resized = Bool

    # model data (resulting from simulations)
    modeldata = Property(Array, allows_none=True)
    _modeldata = Array
    modelnames = List(Str)
    forceupdatemodel = Bool(False)
    A = Float 
    
    # units (handle of units for the axis)
    units = List

    # fit zone (zone taken into account for fitting)
    zone = List

    # can we fit
    fittable = Bool(False)
    
    # clip zone (clipping region)
    clip = List

    # Loading state of this source
    is_loaded = Bool(False)

    # is the replot required?
    data_need_replot = Bool(False)
    model_need_replot = Bool(False)
    
    # should we plot?
    can_plot = Bool(False)

    #===========================================================================
    # plot traits
    #===========================================================================
    # should we show original fid
    unmodified = Bool(False)

    # should we plot the model?
    show_model = Bool(True, 
                      desc='if we want to show the model lines in view plot')

    # should we plot the difference between model and experimental data
    show_diff = Bool(False,
                     desc='if we want to show difference between data '+\
                                                    'and model in view plot')
    # substract baseline
    subtract = Bool(False)

    # autoscaling plot
    autoscale = Bool(True, 
                     desc='an automatic vertical rescaling of the view plot')

    line_attributes = Dict(
            # style, width, color, offset %, previous %
            {'experimental':['Solid', 1.0, wx.Colour(0 , 0 , 0, 255), 0., 0.],
             'baseline':['Solid', 0.65, wx.Colour(255, 255 , 0, 255), 0., 0.],
             'modelsum':['Dashed',0.85, wx.Colour(255, 0 , 0, 255), 0., 0],
             'difference':['Dashdot',0.5, wx.Colour(0, 255 , 0, 255), -30.0, 0.],
             }
    )

    #===========================================================================
    # others
    #===========================================================================
    # Python traits
    _ = Any

    # list of of parameters attributes
    _attribs = List

    #===========================================================================
    # preferences
    #===========================================================================

    #references for the current opened dataset
    sourcepref = Instance(Preferences)        

    #===========================================================================
    # property handlers
    #===========================================================================
    
    @cached_property
    def _get__is_valid(self):
        if not os.path.exists(self._directory):
            return False
        ld = os.listdir(self._directory)
        item = 'fid'
        if item in ld:
            return True
        item = 'ser'
        if item in ld:
            return True        
        return False

    @cached_property
    def _get__message(self):
        if not os.path.exists(self._directory):
            return 'Please, choose a valid Bruker directory containing ' + \
                    'either a fid or a ser file...'
        elif self._is_ok:
            return "loading..."
        if not self._is_valid:
            return 'Sorry, but this directory ' + \
                   'does not contain a valid Bruker fid or ser file'
        else:
            return ''

    def _get_data_orig(self):
        """Read only property
        """
        return self._data_orig.copy()

    def _get_data(self):
        return self._data
    def _set_data(self, value):
        self._data = value

    @cached_property
    def _get_ndims(self):
        """Read only property
        """
        return len(self._data_orig.shape)

    def _set_modeldata(self, value):
        if value is None:
            self._modeldata = np.empty()
        else:
            self._modeldata = value
    def _get_modeldata(self):
        return self._modeldata

    #===========================================================================
    # default_traits_view
    #===========================================================================
    def default_traits_view(self):
        """
        Return the default view of the source traits

        """
        #TODO: could be improved for testing for instance
        return View(
            Item('_directory', style='readonly'),
            Group(
              Item('TD', style='readonly')
            ),
            title="Source of data",
            width=300,
            resizable=True,
        )

    #===========================================================================
    # _load_view
    #===========================================================================
    _is_ok = Bool(False)
    def _load_view(self):
        """ View to choose data location

        """
        return View(
            Item('_directory', style='simple'),
            Item('_message', style='readonly', show_label=False),
            buttons=[
                       Action(name='OK', enabled_when='_is_valid'),
                       'Cancel'
                       ],
            title="Locate Bruker's Sources or Ser's",
            width=600,
            resizable=True,
            handler=_OpenHandler(),
            )
    
    def reset(self):
        """Here the source is reset to its original
        
        """
        self._is_ok = True
        self._import_bruker_source(reset=True)
        
    #===========================================================================
    # _import_bruker_source
    #===========================================================================
    def _import_bruker_source(self, reset=False, lowmem=False):
        """
        Import bruker data and parameters

        """
        self.is_loaded = False

        if (self._is_valid and self._is_ok):

            # read the data
            if not lowmem:
                p, self._data_orig = read(self._directory)
            else:
                p, self._data_orig = read_lowmem(self._directory)
                
            # normalisation of amplitude to ns=1K and rg=1
            self.norm = float(p['acqus']['NS'])*float(p['acqus']['RG'])

            # make this file the last in preferences file
            set_option('application','last_source_file',
                                     self._directory)

            # create the preferences for this source if necessary            
            self._create_source_pref(reset)

            # create a table to handle all parameters
            self._attribs = []

            # create attributes from parameters in the form self.PARAMETER
            self._make_parameters(p)

            #  when just read the data are obviously non transposed       
            self.is_transposed = False

            # and the data are not transformed, so is_freq must be false
            self.is_freq = [False for _i in self._data_orig.shape]  

            # put this attribute in the list of attribs 
            self._attribs.append('is_freq')

            #correct immediately the digital filter
            self._remove_digital_filter()

            # make the working ndarray from the original data
            self.data = self.data_orig  
            self.make_units()
            self.xorig = self.units[-1].ms_scale()
            
            # create some labels for the dimensions
            self._make_labels()

            # modify nuclei informations
            for i in range(self.ndims):
                nucl = self.NUC1[i]
                self.NUC1[i] = nuclei = Isotopes(nucl)   
                logger.info(
                   "This experiment involves %s (I=%s) in %s dimension" % (nucl,
                                                nuclei.spin, self.dimlabels[i]))

            # end the initialization
            logger.debug("Reading data done successfully")    
            self.is_loaded = True
            return True

    #===========================================================================
    # _create_source_pref
    #===========================================================================
    def _create_source_pref(self, reset=False):
        inifile = os.path.join(self._directory, 'preferences.ini')
        
        # erase inifile if reset is required
        if os.path.exists(inifile) and reset:
            os.remove(inifile)
            
        _new = False
        if not os.path.exists(inifile):
            # first time created
            _new = True
        self.sourcepref = Preferences(filename=inifile)
        if _new:
            self.sourcepref.set('processing.forcefid', True)
        self.sourcepref.flush()

    #===========================================================================
    # _make_parameters
    #===========================================================================
    def _make_parameters(self, p):
        """Create self attributes from the NMR parameter dictionary
        """
        parmode = p['acqus']['PARMODE']

        for keys, value in p.iteritems():
            setattr(self, keys, value)  
            
        # create list of parameters with the dimension size 
        # (direct dimension is the last one)
        # and store the attributes name in _attribs
        acqu_selected = acqu_required
        proc_selected = proc_required
        add = get_option('parameters','acqu_selected') 
        if add:
            acqu_selected.extend(add) 
        add = get_option('parameters','proc_selected') 
        if add:
            proc_selected.extend(add)
        
        for key in getattr(self, 'acqus').iterkeys():
            if key not in acqu_selected:
                continue
            setattr(self, key, 
                    [getattr(self, 'acqu%ss' % status[parmode][i])[key]
                                for i in range(parmode, -1, -1)])
            self._attribs.append(key)

        for key in getattr(self, 'procs').iterkeys():
            if key not in proc_selected:
                continue
            setattr(self, key, 
                    [getattr(self, 'proc%ss' % status[parmode][i])[key] 
                                for i in range(parmode, -1, -1)])
            self._attribs.append(key)
            
            # create also a save attribute
            savkey = "%sSAV" % key
            setattr(self, savkey, [0.0 for i in range(parmode, -1, -1)])
            self._attribs.append(savkey)

    #===========================================================================
    # make_units
    #===========================================================================
    def make_units(self):
        """recalculate units
        """
        logger.debug("make units")
        self.units = []
        try:
            for i in range(self.ndims):
                self.units.append(ConvertUnits(self, i))
            if 'units' not in self._attribs: 
                self._attribs.append('units')
        except: 
            # this is more likely because data are not yet fully loaded
            pass
        
        return self.units

    #===========================================================================
    # _make_labels
    #===========================================================================
    def _make_labels(self):
        """create some labels for the dimensions
        """
        self.dimlabels = []
        for i in range(self.ndims):
            if i == self.ndims - 1: 
                self.dimlabels.append('direct')
            else:
                #TODO: implement 3D (in a further version)
                self.dimlabels.append('F1')    
        if not hasattr(self, 'dimlabels'): self._attribs.append('dimlabels')

    #===========================================================================
    # listing
    #===========================================================================
    def listing(self):
        """List NMR parameters for nice printing
        """

        strg = "--acquisition--\n"
        for key in getattr(self, 'acqus').iterkeys():
            strg += "%s: %s\n" % (key, getattr(self, key))

        strg += "\n--processing--\n"
        for key in getattr(self, 'procs').iterkeys():
            strg += "%s: %s\n" % (key, getattr(self, key))

        strg += "\n--pulse program--\n"
        for key in getattr(self, 'pprog').iterkeys():
            strg += "%s: %s\n" % (key, getattr(self, key))

        return strg

    #===========================================================================
    # detect changes
    #===========================================================================
    @on_trait_change('+,+[]')
    def _eventrouter(self, objet=None, name=None, old=None, new=None):
        
        if name.startswith('_data') or name=='_modeldata':
            
            # something has changed  with the source data
#            logger.debug("Source : %s from shape:%s to shape %s"%(name, 
#                                                str(old.shape), str(new.shape)))
            if old is None:
                self.make_units()
                
            elif old.shape != new.shape:
                # we need to recalculate units
                self.make_units()
            
            if name =='_data':
                logger.debug("\nSource : data need replot")
                self.data_need_replot = not self.is_processing

            elif name == '_modeldata':
                logger.debug("\nSource : modeldata need replot")
                self.model_need_replot = not self.is_processing
                    
        else: 
#            logger.debug("Source : %s %s %s"%(name, str(old), str(new)))
            if name == 'unmodified' and not self.is_freq[-1]:
                self.data_need_replot = True 
                
            if name == 'show_model':
                self.model_need_replot = True 
            
            if name == 'show_diff' and self.show_model:
                self.model_need_replot = True 
                
            if name == 'subtract':
                self.data_need_replot = True 
                self.model_need_replot = True
            
            if name == 'forceupdatemodel':
                self.model_need_replot = True
                
            if name == 'is_freq_items':
                self.make_units()
                self.fittable = self.is_freq[-1] 
                if not self.fittable:
                    self.show_model = False
                    
                if new[-1]:
                    logger.debug("reset fit zone and clip setting")
                    #define or redefine the clip limits
                    uc = self.units
                    zone = list(uc[-1].ppm_limits())  
                    # TODO: change this depending on the axis display 
                    self.clip = eval(self.sourcepref.get('processing.clip',
                                                         str(zone)))
                    self.zone = eval(self.sourcepref.get('fitting.zone',
                                                         str(zone)))

    def _is_transposed_changed(self, old, new):
        if old == []:
            return # just initalized do nothing

        if new != old: #True 
            logger.debug("source data transposed?:%s" % str(new))
            # we must exchange the order of the parameters also
            for item in self._attribs:
                val = getattr(self, item) 
                val.reverse()        

    #===========================================================================
    # Object initialisation
    #===========================================================================
    def __init__(self, path=None, lowmem=False, **traits):
        """
        Create and setup the Source object
        
        lowmem loading is experimental and thus not fully working
        """

        super(Source, self).__init__(**traits)

        self._is_ok = False  
        self.is_loaded = False

        if path == 'last':
            last = get_option('application','last_source_file')
            if os.path.exists(last):
                self._is_ok = True
                self._directory = last

        elif path is not None:
            if os.path.exists(path):
                self._is_ok = True
                self._directory = path
            else:
                # try by adding path_of_data
                pathofdata = get_option('application','path_of_data')
                path = os.path.join(pathofdata, path)
                if os.path.exists(path):
                    self._is_ok = True
                    self._directory = path
                else:
                    logger.error('cannot find dataset: %s' % path)
        else:    
            # launch the view for selecting the data
            self.edit_traits(view=self._load_view(), kind='modal')

        self._import_bruker_source(lowmem=lowmem)   
        logger.debug('Source is_loaded : %s' % str(self.is_loaded))

    #===========================================================================
    # copy
    #===========================================================================
    def copy(self):
        """
        make a copy of this source
        
        """
        return deepcopy(self)

    #===========================================================================
    # _remove_digital_filter
    #===========================================================================
    def _remove_digital_filter(self):
        """Remove the digital filter from Bruker data.
        (adapted from nmrglue.fileio.bruker with some modifications
        as the original routine was not working properly for me. 
        https://github.com/jjhelmus/nmrglue - Copyright (C) 2010 Jonathan Helmus
        License: BSD)
        """

        if self.DECIM is None:
            raise ValueError("par does not contain DECIM parameter")

        decim = self.DECIM[-1]

        if self.DSPFVS  is None:
            raise ValueError("par does not contain DSPFVS parameter")

        dspfvs = self.DSPFVS[-1]

        if self.GRPDLY  is None:
            grpdly = 0
        else:
            grpdly = self.GRPDLY[-1]

        bruker_dsp_table = {
            10: { 
                2    : 44.75,
                3    : 33.5,
                4    : 66.625,
                6    : 59.083333333333333,
                8    : 68.5625,
                12   : 60.375,
                16   : 69.53125,
                24   : 61.020833333333333,
                32   : 70.015625,
                48   : 61.34375,
                64   : 70.2578125,
                96   : 61.505208333333333,
                128  : 70.37890625,
                192  : 61.5859375,
                256  : 70.439453125,
                384  : 61.626302083333333,
                512  : 70.4697265625,
                768  : 61.646484375,
                1024 : 70.48486328125,
                1536 : 61.656575520833333,
                2048 : 70.492431640625,
                },
            11: {
                2    : 46.,
                3    : 36.5,
                4    : 48.,
                6    : 50.166666666666667,
                8    : 53.25,
                12   : 69.5,
                16   : 72.25,
                24   : 70.166666666666667,
                32   : 72.75,
                48   : 70.5,
                64   : 73.,
                96   : 70.666666666666667,
                128  : 72.5,
                192  : 71.333333333333333,
                256  : 72.25,
                384  : 71.666666666666667,
                512  : 72.125,
                768  : 71.833333333333333,
                1024 : 72.0625,
                1536 : 71.916666666666667,
                2048 : 72.03125
                },
            12: {
                2    : 46. ,
                3    : 36.5,
                4    : 48.,
                6    : 50.166666666666667,
                8    : 53.25,
                12   : 69.5,
                16   : 71.625,
                24   : 70.166666666666667,
                32   : 72.125,
                48   : 70.5,
                64   : 72.375,
                96   : 70.666666666666667,
                128  : 72.5,
                192  : 71.333333333333333,
                256  : 72.25,
                384  : 71.666666666666667,
                512  : 72.125,
                768  : 71.833333333333333,
                1024 : 72.0625,
                1536 : 71.916666666666667,
                2048 : 72.03125
                },
            13: {
                2    : 2.75,
                3    : 2.8333333333333333,
                4    : 2.875,
                6    : 2.9166666666666667,
                8    : 2.9375,
                12   : 2.9583333333333333,
                16   : 2.96875,
                24   : 2.9791666666666667,
                32   : 2.984375,
                48   : 2.9895833333333333,
                64   : 2.9921875,
                96   : 2.9947916666666667
                } 
            }

        if grpdly > 0:  # use group delay value if provided (not 0 or -1)
            phase = grpdly

        # determind the phase correction
        else:
            if dspfvs >= 14:  # DSPFVS greater than 14 give no phase correction.
                phase = 0.
            else:   # loop up the phase in the table
                if dspfvs not in bruker_dsp_table:
                    logger.warn("dspfvs %d not in lookup table" % dspfvs) 
                    return False
                if decim not in bruker_dsp_table[dspfvs]:
                    logger.warn("decim %d not in lookup table" % decim)
                    return False

                phase = bruker_dsp_table[dspfvs][decim]

        # and the number of points to remove (skip) and add to the beginning
        skip = int(np.floor(phase + 2.))  # round up two integers
        add = int(max(skip - 6, 0))        # 6 less, or 0

        data = _ft(self._data_orig) # the only masai routine 
                                    # that change data_orig
                                    # we do not want to do this again, anyway
        s = float(data.shape[-1])
        ph = 2.*np.pi * phase * np.arange(s) / s
        data = data * np.exp(1j * ph)
        data = _ift(data)

        # add points at the end of the specta to beginning
        # data[..., :add] = data[..., :add]+data[..., :-(add+1):-1]

        # remove points at end of spectra
        self._data_orig = data[..., :-skip]
        self.skip = skip

        # correct TD
        self.TD[-1] = (self.TD[-1] - skip) / 2

#===============================================================================
# _UnitConversion
#===============================================================================
class _UnitConversion():
    """
    Provides methods to convert between common NMR units
    (adapted from nmrglue.unit_conversion in fileiobase module - 
       https://github.com/jjhelmus/nmrglue - Copyright (C) 2010 Jonathan Helmus
     License: BSD)

    Parameters
    ----------
    size : int
        Number of points in dimension (R|I).
    cplex : bool
        True if dimension is complex, False is real.
    sw : float
        Spectral width in Hz.
    obs : float
        Observation frequency in MHz (SFO1 on Bruker)
    car : float
        Carrier frequency in Hz (SR on bruker)

    """
    def __init__(self, size, cplx, sw, obs, car):
        """
        create and set up a unit_conversion object
        """
        # fundamental units
        self._size = size
        self._cplx = cplx
        self._sw = sw
        self._obs = obs
        self._car = car

        # derived units (these are in ppm)
        self._delta = self._sw / (self._size * self._obs)  
        # CF correction (- --> +) 
        # because spectra are not reversed after fourier transform
        self._first = self._car / self._obs - self._delta * self._size / 2.

    # individual unit conversion functions
    def __percent2pts(self, percent):
        return percent * (self._size - 1) / 100.0

    def __pts2percent(self, pts):
        return pts * 100 / (self._size - 1.0)

    def __hz2pts(self, hz):
        return ((hz / self._obs) - self._first) / self._delta

    def __pts2hz(self, pts):
        return (pts * self._delta + self._first) * self._obs

    def __ppm2pts(self, ppm):
        return (ppm - self._first) / self._delta

    def __pts2ppm(self, pts):
        return (pts * self._delta) + self._first

    # times based units: seconds, ms, and us
    def __sec2pts(self, sec):
        return sec * self._sw

    def __pts2sec(self, pts):
        return pts * 1. / self._sw

    def __ms2pts(self, ms):
        return ms * self._sw / 1.e3

    def __pts2ms(self, pts):
        return pts * 1.e3 / self._sw

    def __us2pts(self, us):
        return us * self._sw / 1.e6

    def __pts2us(self, pts):
        return pts * 1.e6 / self._sw

    # routers
    def __unit2pnt(self, val, units):
        """
        Convert units to points
        """
        units = units.upper()
        if units == "PPM":
            pts = self.__ppm2pts(val)
        elif units == "HZ":
            pts = self.__hz2pts(val)
        elif units == "%" or units == "PERCENT":
            pts = self.__percent2pts(val)
        elif units == "SEC" or units == "SECOND" or units == "S":
            pts = self.__sec2pts(val)
        elif units == "MS":
            pts = self.__ms2pts(val)
        elif units == "US":
            pts = self.__us2pts(val)
        else:
            raise ValueError("invalid unit type")
        #if self._cplx:
        #    return pts+round(pts)
        #else:
        return pts

    def __pnt2unit(self, val, units):
        """
        Convert points to units
        """
        units = units.upper()
        #if self._cplx:
        #    val = val-round(val)
        if units == "PPM":
            k = self.__pts2ppm(val)
        elif units == "HZ":
            k = self.__pts2hz(val)
        elif units == "%" or units == "PERCENT":
            k = self.__pts2percent(val)
        elif units == "SEC" or units == "SECOND" or units == "S":
            k = self.__pts2sec(val)
        elif units == "MS":
            k = self.__pts2ms(val)
        elif units == "US":
            k = self.__pts2us(val)
        else:
            raise ValueError("invalid units")
        return k

    def __str2pnt(self, s):
        """
        Convert string with units to points
        """
        units = s.strip(string.digits + string.whitespace + "." + "-").upper()
        val = float(s.strip(string.ascii_letters + string.whitespace + "%"))
        return self.__unit2pnt(val, units)

    def __convert(self, val, unit=None):
        """
        Convert string or value/unit pair
        """
        if type(val) == str:
            return self.__str2pnt(val)
        else:
            if unit == None:
                raise ValueError("invalid unit type")
            return self.__unit2pnt(val, unit)

    # User functions
    def f(self, val, unit=None):
        """
        Convert string or value/unit pair to float
        """
        return self.__convert(val, unit)

    def i(self, val, unit=None):
        """
        Convert string or value/unit pair to integer
        """
        return int(round(self.__convert(val, unit)))

    def ppm(self, val):
        """
        Convert to ppm
        """
        return self.__pnt2unit(val, "PPM")

    def hz(self, val):
        """
        Convert to Hz
        """
        return self.__pnt2unit(val, "HZ")

    def percent(self, val):
        """
        Convert to percent
        """
        return self.__pnt2unit(val, "PERCENT")

    def seconds(self, val):
        """
        Convert to seconds
        """
        return self.__pnt2unit(val, "SEC")

    def sec(self, val):
        """
        Convert to seconds
        """
        return self.__pnt2unit(val, "SEC")

    def ms(self, val):
        """
        Convert to milliseconds (ms)
        """
        return self.__pnt2unit(val, "MS")

    def us(self, val):
        """
        Convert to microseconds (us)
        """
        return self.__pnt2unit(val, "US")

    def unit(self, val, unit):
        """
        Convert val points to unit
        """
        return self.__pnt2unit(val, unit)

    # limits and scales
    def percent_limits(self):
        """
        Return tuple of left and right edges in percent
        """
        return 0.0, 100.0

    def percent_scale(self):
        """
        Return array of percent values
        """
        return np.linspace(0.0, 100.0, self._size)

    def ppm_limits(self):
        """
        Return tuple of left and right edges in ppm
        """
        return self.ppm(0), self.ppm(self._size - 1)

    def ppm_scale(self):
        """
        Return array of ppm values
        """
        x0, x1 = self.ppm_limits()
        return np.linspace(x0, x1, self._size)

    def hz_limits(self):
        """
        Return tuple of left and right edges in Hz
        """
        return self.hz(0), self.hz(self._size - 1)

    def hz_scale(self):
        """
        Return array of Hz values
        """
        x0, x1 = self.hz_limits()
        return np.linspace(x0, x1, self._size)

    def sec_limits(self):
        """
        Return tuple of left and right edges in seconds
        """
        return self.sec(0), self.sec(self._size - 1)

    def sec_scale(self):
        """
        Return array of seconds values
        """
        x0, x1 = self.sec_limits()
        return np.linspace(x0, x1, self._size)

    def ms_limits(self):
        """
        Return tuple of left and right edges in milliseconds
        """
        return self.ms(0), self.ms(self._size - 1)

    def ms_scale(self):
        """
        Return array of seconds values
        """
        x0, x1 = self.ms_limits()
        return np.linspace(x0, x1, self._size)

    def us_limits(self):
        """
        Return tuple of left and right edges in milliseconds
        """
        return self.us(0), self.us(self._size - 1)

    def us_scale(self):
        """
        Return array of seconds values
        """
        x0, x1 = self.us_limits()
        return np.linspace(x0, x1, self._size)

    __call__ = i    # calling the object x is the same as x.i

#===============================================================================
# ConvertUnits
#===============================================================================
class ConvertUnits(HasTraits, _UnitConversion):
    """ 
    Provides methods to convert between common NMR units
    (subclass of nmrglue.fileio.fileiobase.unit_conversion)

    Examples
    --------

    >>> import pylab as pl
    >>> from masai.api import *
    >>> fig = pl.figure(3)
    >>> fd3 = Source(path='test/1') 
    >>> uc = ConvertUnits(fd3)
    >>> p = pl.plot(uc.ms_scale(), fd3.data.real)
    >>> label = pl.xlabel('ms')

    Parameters
    ----------
    fd : Source Instance
        Contains bruker NMR parameters and data
    dim : int, optional, default=-1
        Dimension number to create unit conversion object for. 
        Default is for last (direct) dimension.

    Attributes
    ----------
    sr : float
        Spectrum reference frequency in Hz
        i.e., SR = SFO1 - SF in Bruker Xwinnmr/Topspin

    """    
    _curdim = Enum(-1, 0, 1, 2)

    sf = Property(Float)

    sr = Property(Float)

    def _get_sr(self):
        return (self.fd.SFO1[self._curdim] - self.sf) * 1.e6

    def _set_sr(self, value):
        self.fd.SF[self._curdim] = self.fd.SFO1[self._curdim] - value * 1.e-6

    def _get_sf(self):
        return self.fd.SF[self._curdim]

    def _set_sf(self, value):
        self.fd.SF[self._curdim] = value

    #===========================================================================
    # __init__
    #===========================================================================
    def __init__(self, fd, dim= -1):
        """
        Setup a Unit conversion object for given dimension.
        """
        self.fd = fd
        self._curdim = dim
        size = float(fd.data.shape[dim])
        ndims = fd.ndims
        is_quad = fd.MC2[-1] > 1

        # check for quadrature in indirect dimentions
        if is_quad and (dim != ndims - 1):
            size = size / 2.
            cplx = True
        else:
            cplx = False

        sw = fd.SW_h[dim]
        sfo1 = self.fd.SFO1[self._curdim]

        _UnitConversion.__init__(self, size, cplx, sw, sfo1, self.sr)

