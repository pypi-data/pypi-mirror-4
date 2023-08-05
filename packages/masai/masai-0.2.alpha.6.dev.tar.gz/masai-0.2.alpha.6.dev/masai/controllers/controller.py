#! /usr/bin/env python
#===============================================================================
# main
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
.. _controller:

This module defines objets and methods related to the control of the dataset model.
It is displayed in the left side of main application window

"""
#===============================================================================
# python import
#===============================================================================
import logging
import time

#===============================================================================
# Enthought imports
#===============================================================================
from traits.api import HasTraits, Instance, on_trait_change
from traitsui.api import View, Group

#===============================================================================
# masai imports
#===============================================================================
from masai.utils import InstanceUItem
from fitcontroller import FitController
from plotcontroller import PlotController
from proccontroller import ProcController

#===============================================================================
# logger
#===============================================================================
logger = logging.getLogger()

#===============================================================================
# Controllers
#===============================================================================
class Controllers(HasTraits):
    """Define a sub view for handling the controllers on the left side 
    of the main window

    Three controllers with a GUI displayed in a separate notebook tab are available:
    
        * ProcController, to handle everything related to processing of the spectra
        
        .. seealso:: :ref:`procontroller module <proccontroller>`
           
        * PlotController to manage the display of the data
        
        .. seealso:: :ref:`plotcontroller module <plotcontroller>`
        
        * FitController to set and perform fit of the spectra
        
        .. seealso:: :ref:`fitcontroller module <fitcontroller>`
        
    .. todo::
    
        Add analysis capabilities (integration, peak peaking, and so on...)
    
    """
    #: Instance of class :class:`Source` 
    fd = Instance('masai.api.Source')

    #: Instance of class :class:`ProcController` 
    proccontroller = Instance(ProcController)
    
    #: Instance of class :class:`FitController` 
    fitcontroller = Instance(FitController)
    
    #: Instance of class :class:`PlotController` 
    plotcontroller = Instance(PlotController)
    
    #: Instance of class :class:`ViewPlot` 
    viewplot = Instance('masai.views.ViewPlot')
    
    def default_traits_view(self):
        """Return the main controller view
        
        This view displays a notebook on the left side of the main view 
        with severall controllers (proc, fit and plotcontroller), 
        in a separate tab.
        """
        return View(
               Group(
                    Group(
                         InstanceUItem('proccontroller',),
                         dock='tab',
                         label='Processing',
                         enabled_when='fd.is_loaded and  not _loading',),
                    Group(
                         InstanceUItem('fitcontroller',),
                         dock='tab',
                         label='Modelling',
                         visible_when='fitcontroller',),
                    Group(
                         InstanceUItem('plotcontroller',),
                         label='Plotting',
                         enabled_when='fd.is_loaded and not _loading',),
                    layout='tabbed',
                    show_labels=False,
                    springy=True,)
                ,)

    #===========================================================================
    # events
    #===========================================================================
    @on_trait_change('fd, fd.is_freq_items')
    def _fd_updated(self, objet, name, old, new):
        """The source fd has been changed. 
        
        We need to create the objets if they doesn't exist yet, or simply 
        update the controllers
        
        """  
        if name == 'fd':
            if self.fd.is_loaded:
                logger.debug("controller: source fd has changed")
                self.proccontroller = ProcController(fd=self.fd)
                self.fitcontroller = FitController(fd=self.fd)
                self.plotcontroller = PlotController(fd=self.fd,
                                                        viewplot=self.viewplot)
                
if __name__ == '__main__':
    pass