#! /usr/bin/env python
#===============================================================================
# views.viewplot
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

""" This module essentially define the :class:`ViewPlot` class to plot the data

"""
#===============================================================================
# python import
#===============================================================================
import wx
import os

#===============================================================================
# Enthought imports
#===============================================================================
from traits.api import (HasTraits, Instance, Int, List, Bool, Str, Tuple, Either,
                        Button, Enum, Array, on_trait_change,
                        Property, Float, DelegatesTo)
from traitsui.api import (View, Item, HGroup)
from traitsui.menu import Action, ToolBar, Separator
from pyface.image_resource import ImageResource
from pyface.api import FileDialog, OK

#===============================================================================
# matplotlib, pylab, numpy
#===============================================================================
from matplotlib.figure import Figure, Axes
from matplotlib.colors import ColorConverter
import pylab as pl
import numpy as np

#===============================================================================
# logger
#===============================================================================
import logging
logger = logging.getLogger()

#===============================================================================
# masai imports
#===============================================================================
from masai.api import clipping, findregion
from .plot_editor import PlotEditor
from . import mpl as mpl

#===============================================================================
# constants and utilities
#===============================================================================
IMAGE_LOCATION = os.path.join(os.path.dirname(__file__), "..", "images")

#: conversion between cm and inches
cm2inch = 0.3937008

#: golden number
nb_or = 1.61803399

def mplcolor(color):
    """ Convert a wx color spec. to a matplotlib color spec. 
    
    Parameters
    -----------
    color : :class:`wx.color`
        A wx color definition
    
    Returns
    -------
    ncolor : tuple
        A matplotlib color
        
    
    """
    _color = np.array((1.0, 1.0, 1.0, 1.0))
    _color[:3] = np.asarray(color.Get()) / 255.
    return tuple(_color)

#: Available list of line style
lstyle = {'Solid': '-',
      'Dashed': '--',
      'Dashdot': '-.',
      'Dotted': ':',
      'None': ''}

#===============================================================================
# ViewPlot
#===============================================================================
class ViewPlot(HasTraits):
    """This class handles the plot feature and its view in the GUI application
    
    """
    fd = Instance('masai.fileio.source.Source')

    #: figure instance
    figure = Instance(Figure)
    
    #: size (w,h) of the figure
    #: default: 10 cm, 10cm/nb_or
    figsize = Tuple((10. * cm2inch, 10. * cm2inch / nb_or))
    
    #: dpi (dot per inch) for the figure
    #:     default: 96
    figdpi = Int(96)
    figbackground_color = Tuple(0.95, 0.95, 0.95)  
    # background color of the figure( matplotlib rgb color format)
    figlinewidth = Float(0.1)
    canvas = Property(depends_on='figure')

    # axes and scales
    ax = Instance(Axes)
    axs1 = Instance(Axes)
    axs2 = Instance(Axes)
    axf1 = Instance(Axes)
    axf2 = Instance(Axes)
    tscale = Enum('ms', 's', 'points')
    fscale = Enum('ppm', 'hz', 'points')
    xscale = Str('')
    yscale = Str('')
    xlim = Tuple
    ylim = Tuple
    fdmin = Float
    fdmax = Float

    #data
    x = Array(allows_none=True)
    y = Array(allows_none=True)

    # flags
    showproj = Bool(True)
    showsect = Bool(False)
    showpos = Bool(False)
    showcursor = Bool(False)

    show_model = DelegatesTo('fd')
    show_diff = DelegatesTo('fd')
    unmodified = DelegatesTo('fd')
    subtract = DelegatesTo('fd')
    
    # clipping
    is_clip_applied = Bool(True)
    applyclip = Button("Clip?")
    deleteclip = Button("Undo clip selection?")

    # zone fit
    showzone = Bool(False)

    # action states
    cursor_state = Bool(False)
    crosshairs_state = Bool(False)
    info_state = Bool(False)
    zoom_state = Bool(False)
    zone_state = Bool(False)
    clip_state = Bool(False)
    axzone = List
    axclip = List

    # Toolbar
    toolbar = Instance(ToolBar)

    # Toolbar actions.
    actions = List(Either(Action, Separator))

    # panel printer
    printer = Instance(mpl.FigurePrinter)
    POSTSCRIPT_PRINTING_COMMAND = 'lpr'

    location = Tuple()

    def default_traits_view(self):
        """Display the data and model plots.
        
        """ 
        return View(HGroup(
                           Item("applyclip", show_label=False,),
                           Item("deleteclip", show_label=False),
                           visible_when='not is_clip_applied',
                    ),
                    Item('figure',
                     editor=PlotEditor(),
                     show_label=False,
                     ),
                resizable=True ,
                toolbar=self.toolbar,
                width=600,
                height=500,
                )

    #===========================================================================
    # event router
    #===========================================================================
    @on_trait_change('fd.+')
    def _eventrouter(self, objet=None, name=None, old=None, new=None):
        """Is fired every time a trait associated to the source fd changes.
        wx.CallAfter is used to avoid multiple unecessary calls 
        
        """
        if self.fd.data_need_replot and self.fd.can_plot :
            logger.debug("...viewcontroller: update data plot")
            wx.CallAfter(self._plot1Ddata)
            self.fd.data_need_replot = False
            self._draw()

        if self.fd.model_need_replot and self.fd.can_plot :
            logger.debug("...viewcontroller: update modeldata plot")
            wx.CallAfter(self._plot1Dmodeldata)
            self.fd.model_need_replot = False
            self._draw()

    #===========================================================================
    # figure
    #===========================================================================
    def _figure_default(self):
        return Figure(figsize=self.figsize,
                      dpi=self.figdpi,
                      facecolor=self.figbackground_color,
                      edgecolor=mplcolor(wx.BLACK),
                      linewidth=self.figlinewidth
                      )

    def _get_canvas(self):
        fig = self.figure
        canvas = fig.canvas
        return canvas

    #===========================================================================
    # plot or update plot
    #===========================================================================
    def _resetplot(self):
        logger.debug('viewcontroller: _resetplot')
        n = self.fd.ndims
        if n == 1:
            self._reset1Dplot()
        elif n == 2:
            self._reset2Dplot()
        else:
            raise NotImplementedError, "Not yet: Cannot handle %dD "+\
            " plot higher than 2D" % n

    def _reset1Dplot(self):
        self._create1Daxes() 
        self._create1Dscales()
        self._plot1Ddata()

    def _reset2Dplot(self):
        self._create2Daxes()
        uc = self.fd.units
        self._create2Dscales(uc)
        self._plot2Ddata()

    def _clf(self):
        """Clear the figure
        
        """
        logger.debug('clear figure')
        self.figure.clf()
        self.x = []
        self.y = []

    def _create1Daxes(self):
        """Creates the basic 1D axes of the plot
        
        """
        logger.debug('viewcontroller: _create1Daxes')
        self._clf()
        self.ax = ax = self.figure.add_subplot(111)
        logger.debug('...1D axes created %s' % ax)

    def _create2Daxes(self):
        """Creates the basic axes of the plot
        
        """
        self._clf()
        if not self.showproj: 
            self.ax = ax = self.figure.add_subplot(111)

        else:
            left, width = 0.1, 0.65
            bottom, height = 0.1, 0.65
            bottom_h = left_h = left + width + 0.02
            rectct = [left, bottom, width, height]
            rectf2 = [left, bottom_h, width, 0.2]
            rectf1 = [left_h, bottom, 0.2, height]
            self.ax = ax = self.figure.add_axes(rectct)
            self.axf2 = axf2 = self.figure.add_axes(rectf2, sharex=ax)
            self.axf1 = axf1 = self.figure.add_axes(rectf1, sharey=ax)
            self.axs2 = axs2 = self.figure.add_axes(rectct, sharex=ax)
            self.axs1 = axs1 = self.figure.add_axes(rectct, sharey=ax)

            # no labels
            pl.setp(axf2.get_xticklabels(), visible=False)
            pl.setp(axf2.get_yticklabels(), visible=False)
            pl.setp(axf1.get_xticklabels(), visible=False)
            pl.setp(axf1.get_yticklabels(), visible=False)
            pl.setp(axs2.get_xticklabels(), visible=False)
            pl.setp(axs2.get_yticklabels(), visible=False)
            pl.setp(axs1.get_xticklabels(), visible=False)
            pl.setp(axs1.get_yticklabels(), visible=False)

        logger.debug('2D axes created %s' % ax)

    def _create1Dscales(self):
        """Create new scales

        """
        logger.debug('viewcontroller: _create1Dscales')
        if not hasattr(self,'ax') or self.ax is None:
            logger.debug("ax does not exist yet")
            self._resetplot()

        if self.fd.is_freq[-1]: 
            xscale = self.fscale
        else: 
            xscale = self.tscale

        uc = self.fd.units  
        self.x = getattr(uc[-1], "%s_scale" % xscale)() 
        self.xlim = xlim = getattr(uc[-1], "%s_limits" % xscale)()
        self.ax.set_xlabel(xscale)
        if self.fd.is_freq[-1]: 
            self.ax.set_xlim(xlim[::-1])    
                            # reverse the spectrum plot if it is transformed
                            # as to follow nmr convention
        else:
            self.ax.set_xlim(xlim)

    def _create2Dscales(self, uc):
        """Create new 2D scales

        """
        self._create1Dscales(uc) # for the F2 dimension

        if self.fd.is_freq[-2]: 
            yscale = self.fscale
        else: 
            yscale = self.tscale

        self.y = getattr(uc[-2], "%s_scale" % yscale)()
        self.ylim = getattr(uc[-2], "%s_limits" % yscale)()
        self.ax.set_ylabel(yscale)
        if self.fd.is_freq[0]: 
            self.ax.set_ylim(self.ylim[::-1]) 
            # reverse the spectrum if it is transformed
        else:
            self.ax.set_ylim(self.ylim)  

    def _get_line_from_label(self, label):
        """Knowing the label of line, return the line2D object

        """
        if self.ax is None:
            return False

        for line in self.ax.lines:
            if line.get_label() == label:
                return line
        return False

    def updatelineattr(self, label='experimental', ydata = None):
        """Set the attibute of a given line adressed through its label

        """
        # retrieve the line2D from its name
        line2d = self._get_line_from_label(label)

        if not line2d: 
            # if the line doesn't exist, we have nothing to do here
            return

        #check if the line attributes are in the directory
        #else, we should add them 
        if self.fd.line_attributes.has_key(label):
            line2d.set_linestyle(lstyle[self.fd.line_attributes[label][0]])
            line2d.set_linewidth(self.fd.line_attributes[label][1])
            line2d.set_color(mplcolor(self.fd.line_attributes[label][2]))
            if self.fd.subtract and label == 'baseline':
                # make it disappear when it is subtracted from the data
                line2d.set_linestyle('None')

        else:
            color = line2d.get_color()
            c = []
            for item in ColorConverter().to_rgba(color):
                c.append(int(np.round(item*255)))
            self.fd.line_attributes[label]=[
                        'Solid',0.65, wx.Colour(c[0],c[1],c[2],c[3]), -25, 0]

        if ydata is None:
            # get the line data (which may already contain an offset
            # in principle contained in the last attribute [4]
            prevoffset =self.fd.line_attributes[label][4]
            ydata = line2d.get_ydata()-prevoffset

        # offset given in % of the experimental data
        offpc =self.fd.line_attributes[label][3]
        y = self.fd.data.real
        offset = (np.max(y)-np.min(y))*offpc/100.

        # update the ydata according to the offset
        line2d.set_ydata(ydata + offset)

        #update the previous offset
        self.fd.line_attributes[label][4] = offset

        # visibility
        if label != 'experimental':
            line2d.set_visible(self.show_model)
        if label == 'difference':
            line2d.set_visible(self.show_diff)

        self._draw()

    def _plot1Ddata(self):
        """Plot or update experimental data
        .. todo:: 
            gives the possibility to have several experimental plots

        """
        # get the data to plot
        x = self.x
        y = self.fd.data.real.copy()

        # performs some checkin gon the validity of these data 
        #(x and y should be of same size)
        if x.size != y.shape[-1]:
            self._resetplot()
            return

        # get the line if it already exist or plot it
        line2d = self._get_line_from_label('experimental')
        if not line2d:
            # as the line does not exist we create it for the fist time
            line2d, = self.ax.plot(x, y, 'k', label='experimental')

        # now update the attributes and set the data according to the offset
        if self.subtract:
            y = y - self.fd.modeldata.real[0]
        self.updatelineattr('experimental', ydata = y)

        line2d = self._get_line_from_label('original')
        if not line2d and self.unmodified:
            # as the line does not exist we create it for the fist time
            line2d, = self.ax.plot(self.fd.xorig, self.fd.data_orig.real, 'r', label='original',zorder=-1)
            line2d.set_linestyle(':')
        elif line2d and not self.unmodified:
            line2d.remove()

    def _plot1Dmodeldata(self):
        """Plot or update model data  + baseline

        """
        if not self.fd.fittable:
            return
        
        # get the model data to plot
        x = self.x
        y = self.fd.modeldata.real.copy() 

        # check the validity of the data
        if y.size == 0:
            #no modeldata to plot yet
            return

        if x.size != y.shape[-1]:
            # replot the data first
            # indeed, we need to rescale as x !=y')
            self._plot1Ddata()
            x = self.x

        if not hasattr(self, 'ax'):
            #no ax ... return as nothing can be definitely done (no data)
            return

        # get the previously drawn lines 
        # (include also experimental and difference line)
        modellines = self.ax.get_lines()
        logger.debug("current plotted lines %s"%str(
                                    [line.get_label() for line in modellines]))

        # get the list of name of the model data to plot
        names = self.fd.modelnames
        logger.debug('list of lines to plot %s'%str(names))

        # check if we need to add or removes some line or just update
        for line in modellines:
            # check removing first
            label = line.get_label()
            if label not in ['experimental', 'baseline', 
                             'difference', 'modelsum'] and  label not in names:
                # this line should be removed
                line2d = self._get_line_from_label(label)
                line2d.remove()
                # recursive call to make a full cleaning of the plot
                self._plot1Dmodeldata()
                return

        nm = y.shape[0]
        if nm > 0:
            if self.fd.forceupdatemodel:
                # the model is not yet updated, we nned to do this before plotting
                return
            
            # model lines need to be updated or created
            for i in range(nm):
                line2d = self._get_line_from_label(names[i])
                if not line2d:
                    # as the line does not exist we create it for the fist time
                    try:
                        line2d, = self.ax.plot(x, y[i], ':', label=names[i])
                    except ValueError:
                        return
                    
                # now update the attributes 
                # and set the data according to the offset
                if names[i]=='modelsum' and self.fd.subtract:
                    y[i] = y[i] - self.fd.modeldata.real[0]

                self.updatelineattr(names[i], ydata = y[i])

            # display the difference
            diff = self.fd.data.real - self.fd.modeldata.real[-1]
            line2d = self._get_line_from_label("difference")
            if not line2d:
                # we plot this new line
                line2d, = self.ax.plot(x, diff, label="difference")
            self.updatelineattr('difference', ydata = diff)

    def _plot2Ddata(self):
        """
        
        """        
        x = self.x
        y = self.y
        z = self.fd.data.real
        self.ax.contour(x, y, z)
        if self.showproj:
            f2 = np.sum(z, axis=0)
            f1 = np.sum(z, axis= -1)
            self.axf2.plot(x, f2)
            self.axf1.plot(f1, y)
        # plot model lines
        if self.show_model:
            raise Exception(' DRAW 2D MODEL : not yet implemented')

    #===========================================================================
    # _printer_default
    #===========================================================================

    def _printer_default(self):
        """ Set the printer definition
        
        """
        pData = wx.PrintData()
        pData.SetPaperId(wx.PAPER_A4)
        if callable(getattr(pData, 'SetPrinterCommand', None)):
            pData.SetPrinterCommand(self.POSTSCRIPT_PRINTING_COMMAND)
        return mpl.FigurePrinter(self.canvas, pData)

        #TODO: add menu for printing

    #===========================================================================
    # draw
    #===========================================================================
    def _draw(self, resize=None):
        """Draw the associated figure onto the screen.
        Performs autoscaling if required

        """
        if self.ax is None: 
            logger.debug("...cannot draw because ax is none")
            return

        if (self.fd.autoscale or\
                    (resize == 'vert')) and \
                    (resize != 'hor') and\
                    self.fd.ndims == 1:  

            # Get the maximum and minimum of all displayed lines
            # calculation is done in the fitting zone
            # which should be the whole spectral width if there is no selection 
            uc = self.fd.units
            x = uc[-1].ppm_scale()
            fitzone = findregion(x, self.fd.zone)

            lines = self.ax.get_lines()
            ma = 0.0
            mi = 0.0
            for line2d in lines:
                y = line2d.get_ydata().take(fitzone)
                ma = max(ma,np.max(y))
                mi = min(mi,np.min(y))

            # we allow 2.5% below and above the lines
            am = (ma - mi) * 0.025
            self.ax.set_ylim(mi - am, ma + am)

        if (resize == 'hor'):
            if self.fd.is_freq[-1]: 
                self.ax.set_xlim(self.xlim[::-1])    
                # reverse the spectrum plot if it is transformed

        if (resize == 'vert' and self.fd.ndims == 2):
            if self.fd.is_freq[-2]: 
                self.ax.set_ylim(self.ylim[::-1])    
                # reverse the spectrum plot if it is transformed

        if self.canvas is not None:
            wx.CallAfter(self.canvas.draw)

    def _toolbar_default(self):
        toolbar = ToolBar(*self.actions)
        toolbar.image_size = (24, 24)
        toolbar.show_tool_names = False
        toolbar.show_divider = True
        return toolbar     

    #===========================================================================
    # _actions_default
    #===========================================================================
    def _actions_default(self):

        zoom = \
            Action(
                image=ImageResource('zoom.png', search_path=[IMAGE_LOCATION, "images" ]),
                tooltip="Enable/disable zoom mode",
                style='toggle',
                checked_when='zoom_state',
                defined_when='True',
                enabled_when='not zone_state and not clip_state',
                perform=self._perform_zoom,
            )

        vresize = \
            Action(
                image=ImageResource('varrowsize.png', 
                                    search_path=[IMAGE_LOCATION, "images"]),
                tooltip="Vertical autoscale",
                defined_when='True',
                enabled_when='not zoom_state and not clip_state'+\
                                '  and not zone_state',
                perform=self._perform_vresize,
            )

        hresize = \
            Action(
                image=ImageResource('harrowsize.png', 
                                    search_path=[IMAGE_LOCATION, "images"]),
                tooltip="Horizontal autoscale",
                defined_when='True',
                enabled_when='not zoom_state and not clip_state'+\
                                ' and not zone_state',
                perform=self._perform_hresize,
            )         

        zone = \
            Action(
                image=ImageResource('zone.png', search_path=[IMAGE_LOCATION, "images"]),
                tooltip="Select a fitting region",
                defined_when='True',
                enabled_when='not zoom_state and not clip_state',
                style='toggle',
                checked_when='zone_state',
                perform=self._perform_zone,
            )

        clip = \
            Action(
                image=ImageResource('cutter.png', 
                                    search_path=[IMAGE_LOCATION, "images"]),
                tooltip="horizontally clip spectra to a selected region",
                defined_when='True',
                enabled_when='not zoom_state and not zone_state',
                style='toggle',
                checked_when='clip_state',
                perform=self._perform_clip,
            )  

        info = \
            Action(
                image=ImageResource('info.png', search_path=[IMAGE_LOCATION, "images" ]),
                tooltip="Show/hide info reporting",
                style='toggle',
                checked=False,
                defined_when='True',
                enabled_when='True',
                perform=self._perform_info,
            )

        do_print = \
            Action(
                image=ImageResource('printer.png',
                                    search_path=[IMAGE_LOCATION, "images"]),
                tooltip="Print figure",
                defined_when='True',
                enabled_when='True',
                perform=self._perform_do_print,
            )

        return [Separator(), zoom,
                             hresize,
                             vresize,
                Separator(), clip,
                Separator(), zone,
                Separator(), info,
                Separator(), do_print]

    def _perform_zoom(self):
        self.zoom_state = not self.zoom_state
        self.canvas.set_zoom(self.zoom_state)
        self.canvas.set_crosshairs(self.zoom_state)
        self.canvas.set_selection(self.zoom_state)

    def _perform_vresize(self):
        self._draw(resize='vert')

    def _perform_hresize(self):
        self._draw(resize='hor')

    def _perform_autoscale(self):
        self.autoscale = True
        self._draw()

    def _perform_info(self):
        self.info_state = not self.info_state
        self.canvas.set_location(self.info_state)

    def _perform_do_print(self):
        #self.printer.printFigure(self.figure)
        dlg = FileDialog(parent=self.canvas, action='save as', wildcard="*.pdf")
        if dlg.open() == OK:
            self.figure.savefig(dlg.path, dpi=300, 
                            orientation='paysage', papertype='A4', format='pdf')
#        savefig(fname, dpi=None, facecolor='w', edgecolor='w',
#        orientation='portrait', papertype=None, format=None,
#        transparent=False, bbox_inches=None, pad_inches=0.1)

    def _perform_zone(self):
        self.zone_state = not self.zone_state
        self.clip_state = False
        self.canvas.set_zone(True) 
        mpl.EVT_SELECTION(self.figure.canvas, -1, self._onselectfitzone)

    def _perform_clip(self): 
        self.clip_state = not self.clip_state
        self.zone_state = False
        self.canvas.set_zone(self.clip_state) # same procedure as for zone
        mpl.EVT_SELECTION(self.figure.canvas, -1, self._onselectclipzone)

    def _onselectfitzone(self, val):
        limits = self.ax.get_xlim()
        xmin = val.x1data
        xmax = val.x2data

        if xmin > xmax:
            xmin, xmax = (xmin, xmax)[::-1]

        x = self.x
        indmin, indmax = np.searchsorted(x, (xmin, xmax))
        indmax = min(len(x) - 1, indmax)

        self.fd.zone = zone = list((x[indmin], x[indmax]))
        
        for item in self.axzone:
            item.set_visible(False)

        # warning the spectrum is reversed, this is why we invert the limits
        self.axzone.append(self.ax.axvspan(limits[-1], zone[0], 
                                facecolor='lightyellow', hatch='/', alpha=0.3))
        self.axzone.append(self.ax.axvspan(zone[-1], limits[0], 
                                facecolor='lightyellow', hatch='\\', alpha=0.3))
                
        wx.CallAfter(self._draw)

        self.zone_state = False
        self.canvas.set_zone(False)     
        mpl.EVT_SELECTION(self.figure.canvas, -1, None)

        self.fd.forceupdatemodel = True

    def _onselectclipzone(self, val=None, delete=False):

        limits = self.ax.get_xlim()
        if not delete:
            xmin = val.x1data
            xmax = val.x2data
        else:
            xmin = min(limits)
            xmax = max(limits)

        if xmin > xmax:
            xmin, xmax = (xmin, xmax)[::-1]

        x = self.x
        indmin, indmax = np.searchsorted(x, (xmin, xmax))
        indmax = min(len(x) - 1, indmax)

        self.fd.clip = clip = list((x[indmin], x[indmax]))
        for item in self.axclip:
            item.set_visible(False)

        # warning the spectrum is reversed, this is why we invert the limits
        self.axclip.append(self.ax.axvspan(limits[-1], clip[0], facecolor='red', hatch='.', alpha=0.8))
        self.axclip.append(self.ax.axvspan(clip[-1], limits[0], facecolor='red', hatch='.', alpha=0.8))
        wx.CallAfter(self._draw)

        self.clip_state = False
        self.canvas.set_zone(False)     
        mpl.EVT_SELECTION(self.figure.canvas, -1, None)

        self.is_clip_applied = False
        
    def _applyclip_fired(self):
        self.fd.can_plot = False
        clipping(self.fd)
        uc = self.fd.units
        self.fd.clip = list(uc[-1].ppm_limits())
        #FIXME: check this because when apply several times, low limits changes!!!!
        self.fd.sourcepref.set('processing.clip', self.fd.clip)
        self.fd.sourcepref.flush()
        self.fd.can_plot = True
        self.is_clip_applied = True
        wx.CallAfter(self._draw)
                
    def _deleteclip_fired(self):
        self._onselectclipzone(delete=True)
        self.fd.sourcepref.set('processing.clip', self.fd.clip)
        self.fd.sourcepref.flush()
        self.is_clip_applied = True

#we could also use
#self.printer.pageSetup()
#self.printer.previewFigure(self.get_figure())    
