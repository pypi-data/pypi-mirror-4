#! /usr/bin/env python
#===============================================================================
# views.plot_editor
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

#===============================================================================
# python import
#===============================================================================
import wx

#===============================================================================
# enthought import
#===============================================================================
from enthought.traits.ui.wx.editor import Editor
from enthought.traits.ui.wx.basic_editor_factory import BasicEditorFactory
from enthought.traits.api import Instance

#===============================================================================
# local import
#===============================================================================
import mpl #TODO: traitify mpl

#===============================================================================
# _PlotEditor
#===============================================================================
class _PlotEditor(Editor):

    scrollable = True
    
    #===========================================================================
    # init
    #===========================================================================
    def init(self, parent):
        self.control = self._create_canvas(parent)
        self.set_tooltip()
        
    #===========================================================================
    # update_editor
    #===========================================================================
    def update_editor(self):
        pass

    #===========================================================================
    # _create_canvas
    #===========================================================================
    def _create_canvas(self, parent):
        """ Create the MPL canvas. """
        
        # The panel lets us add additional controls.
        panel = wx.Panel(parent, -1, style=wx.CLIP_CHILDREN)
        sizer = wx.BoxSizer(wx.VERTICAL)
        panel.SetSizer(sizer)
        canvas = mpl.PlotPanel(panel, -1, figure=self.value)
        sizer.Add(canvas, 1, wx.LEFT | wx.TOP | wx.GROW)
        self.value.canvas.SetMinSize((50, 50))
                
        return panel
       
#===============================================================================
# PlotEditor
#===============================================================================
class PlotEditor(BasicEditorFactory):

    klass = _PlotEditor





