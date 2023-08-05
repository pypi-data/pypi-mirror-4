#! /usr/bin/env python
#===============================================================================
# controllers.plotcontroller
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
.. _plotcontroller:

This module defines objets and methods related to the plotting of the
datasets.

"""
import wx

#===============================================================================
# Enthought imports
#===============================================================================
from traits.api import (HasTraits, Instance, Range, Bool, Int, Enum,
                        Float, Button, on_trait_change, Color, ListFloat,
                        List, Property, Str,
                        DelegatesTo)
from traitsui.api import (View, Item, Group, VGroup, HGroup, HFlow,
                          spring, ScrubberEditor, ColorEditor,
                          Handler, EnumEditor)

#===============================================================================
# numpy, mathplotlib
#===============================================================================
import numpy as np
from masai.views.viewplot import mplcolor, lstyle

#===============================================================================
# logger
#===============================================================================
import logging
logger = logging.getLogger()

#===============================================================================
# masai imports
#===============================================================================

#===============================================================================
# PlotController
#===============================================================================
class PlotController(HasTraits):
    """Control viewplot appearance and behaviour 

    """
    # the source of data
    fd = Instance('masai.api.Source')
    viewplot = Instance('masai.views.ViewPlot')

    show_model = DelegatesTo('fd')
    show_diff = DelegatesTo('fd')
    autoscale = DelegatesTo('fd')
    subtract = DelegatesTo('fd')
    fittable = DelegatesTo('fd')
    unmodified = DelegatesTo('fd')
    
    data_width = Range(.1, None, .8)
    data_color = Color(wx.Colour(128, 128, 128, 255))
    data_style = Enum(lstyle.keys())
    data_offset = Float(.0)

    diff_width = Range(.1, None, .8)
    diff_color = Color(wx.Colour(128, 128, 128, 255))
    diff_style = Enum(lstyle.keys())
    diff_offset = Float(.0)

    modelnames = DelegatesTo('fd')
    line = Str('baseline')

    width = Range(.1, None, .8)
    color = Color
    style = Enum('Solid', lstyle.keys())
    offset = Float(.0)

    grpexp = VGroup(
                    HGroup(
                           Item('data_style', label='style', width=30),
                           Item('data_color', label='color', width=100,
                                editor=ColorEditor()),
                           ),
                    HGroup(
                           Item('data_width', label='width', width=30,
                                editor=ScrubberEditor(increment=.1,
                                                      hover_color=0xFFFFFF,
                                                      active_color=0xB0DD8E),
                                ),
                           Item('data_offset', label='offset(%)', width=30,
                                editor=ScrubberEditor(increment=.5,
                                                      hover_color=0xFFFFFF,
                                                      active_color=0xB0DD8E),
                                ),
                           ),
                    Item('subtract', label='Subtract baseline',
                         visible_when='modelnames and fittable'),
                    Item('unmodified', label='show original data',
                         visible_when = 'not fittable'),
                    label='Experimental',
                    show_border=True,
                    )

    grpmod = VGroup(
                    Item(name='line',
                         editor=EnumEditor(name='modelnames'),
                         ),
                    VGroup(
                           HGroup(
                                  Item(name='style',width=30),
                                  Item(name='color', width=100,
                                       editor=ColorEditor()
                                       ),
                                  ),
                           HGroup(
                                  Item(name='width', width=30,
                                       editor=ScrubberEditor(increment=.1,
                                                        hover_color=0xFFFFFF,
                                                        active_color=0xB0DD8E),
                                       ),
                                  Item(name='offset',
                                       label='offset(%)', width=30,
                                       editor=ScrubberEditor(increment=.5,
                                                        hover_color=0xFFFFFF,
                                                        active_color=0xB0DD8E),
                                       ),
                                  ),
                           enabled_when='not (subtract and line=="baseline")',
                           ),
                    label='Models',
                    show_border=True,
                    visible_when='fittable',
                    ),

    grpdif = VGroup(
                    HGroup(
                           Item('diff_style', label='style', width=30),
                           Item('diff_color', label='color', width=100,
                                editor=ColorEditor()
                                ),
                           ),
                    HGroup(
                           Item('diff_width', label='width', width=30,
                                editor=ScrubberEditor(increment=.1,
                                                      hover_color=0xFFFFFF,
                                                      active_color=0xB0DD8E),
                                ),
                           Item('diff_offset',
                                label='offset(%)', width=30,
                                editor=ScrubberEditor(increment=.5,
                                                      hover_color=0xFFFFFF,
                                                      active_color=0xB0DD8E),
                                ),
                           ),
                    label='Difference',
                    show_border=True,
                    visible_when="show_diff and modelnames and fittable"
                    )

    grpsho = HGroup(
                    Item("show_model", label="Show model"),
                    Item("show_diff", label="Show difference",
                         visible_when='show_model',
                         ),
                    visible_when='fittable',
                    label='Model',
                    show_border=True,
                    )

    grpmis = HGroup(
                    Item("autoscale", label='Auto scale y axis?',
                         visible_when='fd.ndims==1'),
                    label='Miscellaneous',
                    show_border=True,
                    )
    
    view = View(
                Group(
                      grpexp,
                      grpmod,
                      grpdif,
                      grpsho,
                      grpmis,
                      orientation='vertical',
                      ),
                width=350,
                resizable=True,
                )

    def _line_default(self):
        return 'baseline'

    def _color__default(self):
        return self.fd.line_attributes[self.line][2]

    def _style_default(self):
        return self.fd.line_attributes[self.line][0]

    def _width_default(self):
        return self.fd.line_attributes[self.line][1]

    def _offset_default(self):
        return self.fd.line_attributes[self.line][3]  

    def _anytrait_changed(self, name, old, new):
        """Detect all changes in the plotcontroller traits
        """
        logger.debug ("%s, %s, %s" % (name, str(old), str(new)))

        if self.viewplot is None or self.fd is None:
            return
        
        if name == 'data_style':
            self.fd.line_attributes['experimental'][0] = self.data_style
            self.viewplot.updatelineattr('experimental')

        if name == 'data_width':
            self.fd.line_attributes['experimental'][1] = self.data_width
            self.viewplot.updatelineattr('experimental')

        if name == 'data_color_':
            self.fd.line_attributes['experimental'][2] = self.data_color_
            self.viewplot.updatelineattr('experimental')

        if name == 'data_offset':
            self.fd.line_attributes['experimental'][3] = self.data_offset
            self.viewplot.updatelineattr('experimental')

        if name == 'diff_style':
            self.fd.line_attributes['difference'][0] = self.diff_style
            self.viewplot.updatelineattr('difference')

        if name == 'diff_width':
            self.fd.line_attributes['difference'][1] = self.diff_width
            self.viewplot.updatelineattr('difference')

        if name == 'diff_color_':
            self.fd.line_attributes['difference'][2] = self.diff_color_
            self.viewplot.updatelineattr('difference')

        if name == 'diff_offset':
            self.fd.line_attributes['difference'][3] = self.diff_offset
            self.viewplot.updatelineattr('difference')

        if name == 'fd':
            # initialization 
            self.data_style = self.fd.line_attributes['experimental'][0]
            self.data_width = self.fd.line_attributes['experimental'][1]
            # warning data_color must be followed by a _
            # if not the property is not set (good to know)
            self.data_color_ = self.fd.line_attributes['experimental'][2]
            self.data_offset = self.fd.line_attributes['experimental'][3]
            self.viewplot.updatelineattr('experimental')

            self.diff_style = self.fd.line_attributes['difference'][0]
            self.diff_width = self.fd.line_attributes['difference'][1]
            self.diff_color_ = self.fd.line_attributes['difference'][2]
            self.diff_offset = self.fd.line_attributes['difference'][3]
            self.viewplot.updatelineattr('difference')

        if name == 'line':
            line = self.line
            self.color_ = self.fd.line_attributes[line][2]
            self.color = self.fd.line_attributes[line][2]
            self.offset = self.fd.line_attributes[line][3]
            self.style = self.fd.line_attributes[line][0]
            self.width = self.fd.line_attributes[line][1]
            self.viewplot.updatelineattr(self.line)     

        if name == 'style':
            self.fd.line_attributes[self.line][0] = self.style
            self.viewplot.updatelineattr(self.line)

        if name == 'width':
            self.fd.line_attributes[self.line][1] = self.width
            self.viewplot.updatelineattr(self.line)

        if name == 'color_':
            self.fd.line_attributes[self.line][2] = self.color_
            self.viewplot.updatelineattr(self.line)

        if name == 'offset':    
            self.fd.line_attributes[self.line][3] = self.offset
            self.viewplot.updatelineattr(self.line)
