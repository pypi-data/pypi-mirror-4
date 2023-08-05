#! /usr/bin/env python
#===============================================================================
# controllers.proccontroller
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
.. _proccontroller:

This module defines objets and methods related to the processing of the
datasets

"""
#===============================================================================
# Enthought imports
#===============================================================================
from traits.api import (HasTraits, Instance, Range, Bool, Int, Enum,
                        Float, Button, on_trait_change)
from traitsui.api import (View, Item, Group, VGroup, HGroup,
                          spring, ScrubberEditor)
     
#===============================================================================
# numpy
#===============================================================================
import numpy as np

#===============================================================================
# logger
#===============================================================================
import logging
logger = logging.getLogger()

#===============================================================================
# masai imports
#===============================================================================
from masai.api import (tdeff, em, pk, apk, efp, largest_power_of_2)

#===============================================================================
# formatter
#===============================================================================
def formatter(value):
    """Format of an Item
    """
    if isinstance(value, float):
        return str("%.3f" % value)
    else:
        return str(value)
     
#===============================================================================
# ProcController
#===============================================================================
class ProcController(HasTraits):
    """
    This controller hosts the method for processing the data displyed in the 
    viewplot..
    
    """
    # the figure where to plot our data
    #viewplot = Instance(ViewPlot)

    # the source of data
    fd = Instance('masai.fileio.source.Source')
    
    #===========================================================================
    # # other traits for processing    
    #===========================================================================
    autoprocessing = Bool(False)
    td = Int
    
    tdeff = Range(low=256)
    def _tdeff_changed(self):
        self.fd.sourcepref.set('processing.tdeff', self.tdeff)
        self.fd.sourcepref.flush()
        self.fd.TDeff[-1] = self.tdeff
        tdeff(self.fd)
        
    si = Enum(2 ** 10, 2 ** 11, 2 ** 12, 2 ** 13, 2 ** 14, 2 ** 15, 2 ** 16)
    def _si_changed(self):
        self.fd.sourcepref.set('processing.si', self.si)
        self.fd.sourcepref.flush()
        self.fd.SI[-1] = self.si
    
    lb = Range(low=0.)
    def _lb_changed(self):
        self.fd.sourcepref.set('processing.lb', self.lb)
        self.fd.sourcepref.flush()
        self.fd.LB[-1]=self.lb
        em(self.fd)

    ph0 = Range(0., +360.)
    ph1 = Float
    ph0inc = 10.
    ph1inc = 10.

    def _ph0_changed(self):
        if not self.fd.is_freq[-1]: return
        self.fd.PHC0[-1] = self.ph0
        self.fd.sourcepref.set('processing.ph0', self.ph0)
        self.fd.sourcepref.flush()
        pk(self.fd)
        
    def _ph1_changed(self):
        if not self.fd.is_freq[-1]: return 
        self.fd.PHC1[-1] = self.ph1
        self.fd.sourcepref.set('processing.ph1', self.ph1) 
        si = self.fd.data.shape[-1]
        pcor = np.deg2rad(self.ph1 - self.fd.PHC1SAV[-1])*\
                                             float(self.fd.phcursor) / float(si)
        self.ph0 = (self.ph0 - np.rad2deg(pcor)) % 360.
        
    apk = Button("APK")
    def _apk_fired(self):
        apk(self.fd)
        self.ph0 = self.fd.PHC0[-1] % 360.0 
        
    inv = Button(u'ADD 180\u00B0')
    def _inv_fired(self):
        self.ph0 = (self.fd.PHC0[-1] - 180.) % 360.

    quad = Button(u'ADD 90\u00B0')
    def _quad_fired(self):
        self.ph0 = (self.fd.PHC0[-1] + 90.) % 360.
                              
    efp = Button("EFP")
    def _efp_fired(self):
        self.fd.can_plot = False
        efp(self.fd) 
        self.fd.sourcepref.set('processing.forcefid', False)
        self.fd.sourcepref.flush()
        self.fd.can_plot = True
                                                                 
    reset = Button("RESET TO ORIGINAL")    
    def _reset_fired(self):
        self.fd.reset()
        self.resetpar()

#    baseline = Instance(Baseline)
#    def _baseline_default(self):
#        return Baseline(fd=self.fd)
#    
    #===========================================================================
    # view
    #===========================================================================
    def default_traits_view(self):
        return View(
              Group(
                    VGroup(HGroup(
                           Item('ph0', width=100,
                                   editor=ScrubberEditor(
                                                        format_func=formatter,
                                                        increment=.5,
                                                        hover_color=0xFFFFFF,
                                                        active_color=0xB0DD8E),
                                ),
                           Item('ph1', width=100,
                                   editor=ScrubberEditor(
                                                        format_func=formatter,
                                                        increment=1.0,
                                                        hover_color=0xFFFFFF,
                                                        active_color=0xB0DD8E)

                            ),
                           ),
                           HGroup(
                                  spring,
                                  Item('apk', show_label=False),
                                  Item('quad', show_label=False),
                                  Item('inv', show_label=False),
                           ),
                           Item('_'),
                           enabled_when='fd.is_freq[-1]',
                           label='Phases',
                    ),
                    VGroup(
                        HGroup(
                           Item('lb',
                                editor=ScrubberEditor(
                                                      format_str="%.2f",
                                                      increment=.5,
                                                      hover_color=0xFFFFFF,
                                                      active_color=0xB0DD8E)
                                ),
                           #Item('reducesampling', label='Reduce sampling'),
                           Item('tdeff', label='effective TD',
                                 editor=ScrubberEditor(
                                                       format_str="%d",
                                                       increment=1,
                                                       hover_color=0xFFFFFF,
                                                       active_color=0xB0DD8E)),
                           spring,
                        ),
                       Item('_'),
                       label='Apodization',
                       enabled_when='not fd.is_freq[-1]',
                    ),
                    VGroup(
                        HGroup(
                           Item('si', label='transformed size'),
                           Item('efp', show_label=False),
                           spring,
                        ),
                       Item('_'),
                       enabled_when='not fd.is_freq[-1]',
                       label='Transforms',
                    ),
                  Item('reset', show_label=False),
                  visible_when='fd'
               ),
            resizable=True,
            width=0.33, #TODO: find the way to set the initial width
            height=1.,
#            handler = ProcControlHandler()
            )
        
    def resetpar(self):
        """Reset some parmeters to their default value (
           (or the preferred value in the preference file whne it exists)
           
        """
        self.tdeff = self.fd.TDeff[-1] = int(self.fd.sourcepref.get(
                   'processing.tdeff', max(self.fd.TD[-1], self.fd.TDeff[-1])))
        self.si = self.fd.SI[-1] = int(self.fd.sourcepref.get('processing.si', 
                                        largest_power_of_2(self.fd.TD[-1] * 2)))
        self.lb = self.fd.LB[-1] = float(self.fd.sourcepref.get('processing.lb',
                                                                self.fd.LB[-1]))
        self.ph0 = self.fd.PHC0[-1] = float(self.fd.sourcepref.get(
                                    'processing.ph0', self.fd.PHC0[-1])) % 360.0
        self.ph1 = self.fd.PHC1[-1] = float(self.fd.sourcepref.get(
                                            'processing.ph1', self.fd.PHC1[-1]))
        
    #===========================================================================
    # event router
    #===========================================================================
    @on_trait_change('fd.+')
    def _eventrouter(self, objet, name, old, new):
        
        if not self.fd.is_loaded: 
            # we return if the source is not valid
            return   
         
        if name == "fd":
            # if we have this event, 
            # this is because the fd source has just been updated
            # get previous values from preference files
            logger.debug("proccontroller: %s from %s to %s" % (name, str(old), 
                                                               str(new)))

            self.resetpar()        
