#! /usr/bin/env python
# -*- coding: utf-8 -*-
#===============================================================================
# masaigui
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

The :mod:`masaigui` module is the main entry point of the **MASAI** 
GUI (Graphical User Interface) application.

The GUI can be started in the terminal by typing ::

    $ python masaigui.py

assuming that the current directory is the **masai** application directory .

Some copyright information and the version number are witten in the terminal 
while the application is loading. 

To display some debugging messages while running **MASAI** one can use the 
*--debug* flag::

    $ python masaigui.py --debug
    
The cost of this may be a significant slowing down of the program.

"""

#===============================================================================
# print version number at the start of the program
#===============================================================================
from masai.version import _TITLE_, _VERSION_, _REVISION_, _COPYRIGHT_
print "%s\nversion : %s-%s\nCopyrigth (c)%s" % (_TITLE_, _VERSION_, 
                                                _REVISION_, _COPYRIGHT_)

#===============================================================================
# python import
#===============================================================================
import os
import sys
import logging
import time

#===============================================================================
# logger
#===============================================================================
logger = logging.getLogger()
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.INFO)
for arg in sys.argv[1:]:
    if arg == '--debug': 
        logger.setLevel(logging.DEBUG)
        logger.debug('Masai is running in DEBUGGING mode.')

#===============================================================================
# PYTHONPATH
#===============================================================================
# in case masai was not yet installed using setup 
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
logger.debug(sys.path)

#===============================================================================
# Enthought imports
#===============================================================================
from traits.api import (HasTraits, Instance, Property, DelegatesTo,
                        on_trait_change, HTML)
from traitsui.api import (View, HSplit, Handler, auto_close_message,
                          ImageEditor, Group, Label, Item, UItem, HTMLEditor)
from traitsui.menu import MenuBar, Menu, Action
from pyface.api import ImageResource, SplashScreen
from pyface.api import confirm, YES
from pyface.api import GUI
from apptools.preferences.api import (set_default_preferences,
                                      get_default_preferences, Preferences)

#===============================================================================
# masai imports
#===============================================================================
from masai.api import Source, efp, largest_power_of_2
from masai.controllers import Controllers
from masai.views import ViewPlot
from masai.options import edit_options
from masai.utils import InstanceUItem

#===============================================================================
# splash screen and GUI (#TODO: make a pyface application)
#===============================================================================
splash_screen = SplashScreen(image=ImageResource('images/splash'))
_gui = GUI(splash_screen=splash_screen)

#===============================================================================
# constants
#===============================================================================
license_label = \
"""
<html><body>
<H2>Masa&iuml;, a framework for processing and modelling of solid state NMR spectra</H2>

<b>Copyright: &copy; %(copyright)s</b>

<b>version: %(version)s.%(revision)s</b>

<b>email: </b> <a href='mailto:christian.fernandez@ensicaen.fr'>
christian.fernandez@ensicaen.fr</a>
 
This software is a computer program whose purpose is to perform 
processings and analysis of solid-state NMR spectra.
 
This software is governed by the CeCILL-B license under French law and abiding 
by the rules of distribution of free software.  
You can  use, modify and/or redistribute the software under the terms of 
the CeCILL-B license as circulated by CEA, CNRS and INRIA at the 
following URL: <a href='http://www.cecill.info'>http://www.cecill.info</a>. 
 
As a counterpart to the access to the source code and rights to copy, modify 
and redistribute granted by the license, users are provided only
with a limited warranty  and the software's author,  the holder of 
the economic rights,  and the successive licensors  have only  limited
liability. 
 
In this respect, the user's attention is drawn to the risks associated
with loading,  using,  modifying and/or developing or reproducing the
software by the user in light of its specific status of free software,
that may mean  that it is complicated to manipulate,  and  that  also
therefore means  that it is reserved for developers  and  experienced
professionals having in-depth computer knowledge. Users are therefore
encouraged to load and test the software's suitability as regards their
requirements in conditions enabling the security of their systems and/or 
data to be ensured and,  more generally, to use and operate it in the 
same conditions as regards security. 
 
The fact that you are presently reading this means that you have had
knowledge of the CeCILL-B license and that you accept its terms.
 
</body></html>
"""%{'copyright': _COPYRIGHT_, 'version':_VERSION_, 'revision':_REVISION_}
  
contact_label = """
http://github.com/fernandezc/masai
"""
pathini = os.path.join(os.path.expanduser('~'), '.masai')

default_ini = """
[application]
last_source_file = 
path_of_data = 
width = 1.0
height = 0.8

[processing]
process_automatically = True

[plot]
bgcolor = "(255, 255, 255, 255)"
fgcolor = "(0, 0, 0, 255)"
"""

#===============================================================================
# prepare ini
#===============================================================================
if not os.path.exists(pathini):
    logger.debug('create hidden directory %s' % pathini)
    os.mkdir(pathini)

inifile = os.path.join(pathini, 'masai.ini')
if not os.path.exists(inifile): 
    logger.info('open masai.ini in %s' % pathini)
    with open(inifile, 'w') as f:
        f.write(default_ini)  

set_default_preferences(Preferences(filename=inifile))

#===============================================================================
# MasaiGuiMainWindow
#===============================================================================
class MasaiGuiMainWindow(HasTraits):
    """ The Masai main GUI window.
    
    here go the instructions to create and destroy the application.
    General menu are also defined here.

    """
    
    #: Instance of :class:`ViewPlot`, where the plot of the experimental data 
    #: and modelled data are displayed 
    viewplot = Instance(ViewPlot)
    
    #: Instance of :class:`Controllers`, allowing action on the data and the plot view.
    controllers = Instance(Controllers)
    
    #: Instance of the :class:`Source`, which store the experimental data and the modelled data as well.
    fd = Instance(Source)
    
    #: Instance of :class:`Preferences`, which handle the main application preferences
    applicationpref = Instance(Preferences)

    #: Height of the main window (will be read from preference)
    height = Property
    
    #: Width of the main window (will be read from preference)
    width = Property
    
    # Are we loading the source and doing the first processings
    _loading = True
    
    # can we plot the data?
    can_plot = DelegatesTo('fd')

    # for the about dialog
    license = HTML(license_label)

    #===========================================================================
    # properties
    #===========================================================================
    def _get_height(self):
        """Height of the main window
        """
        return float(self.applicationpref.get('application.height'))

    def _get_width(self):
        """Width of the main window
        """
        return float(self.applicationpref.get('application.width'))

    #TODO: write the current value back to the preference.
    
    #===========================================================================
    # preferences
    #===========================================================================
    def _applicationpref_default(self):
        """Get the preferences for the application

        """
        return get_default_preferences()

    #===========================================================================
    # menus    
    #===========================================================================
    _open_action = Action(name="&New Source",
                          accelerator="Ctrl+N",
                          action="_performs_open_fd",
                          image=ImageResource("images/open.png"),
                          tooltip=u"Open a different dataset")
    
    _options_action = Action(name="&Options",
                          accelerator="Ctrl+O",
                          action="_performs_options",
                          image=ImageResource("images/options.png"),
                          tooltip=u"Open the preference manager")
    
    _exit_action = Action(name="&Quit",
                          accelerator="Ctrl+Q",
                          action="close",
                          image=ImageResource("images/exit")) 
    
    _help_action = Action(name="&Help",
                          accelerator="Ctrl+H",
                          action="_performs_show_help",
                          image=ImageResource("images/help"),
                          tooltip=u"Open help in an external web browser")

    _about_action = Action(name=u"About Masai",
                          action="_performs_show_about",
                          image=ImageResource("images/about"),
                          tooltip=u"Various information about Masa\u00EF")

    #: Menu entry used to show the About window or Help Browser.
    help_menu = Menu("|",
                     _help_action, "_",
                     _about_action,
                     name="&Help")

    #: Menu entry used to show the Preferences pages
    options_menu = Menu("|",
                     _options_action,
                     name="Options")

    #: Menu used to open new source dataset, print data or the close the application
    file_menu = Menu("|",
                     _open_action, '_',
                     _exit_action,
                     name="File")
    #: the main menubar
    menubar = MenuBar(file_menu, options_menu, help_menu)

    def _performs_open_fd(self):
        """Open a new source of data

        """
        #before we open a new source, we must stop current timer threads or
        # it will stay running until killing of the program.
        self.controllers.fitcontroller.paramscript.timer.stop()
        
        del self.fd
        # Then we can proceed with a new source
        fd = Source()
        if not fd.is_loaded:
            # this is a problem! Cancel may have been pushed,
            # we need to reload the last Source.
            fd = Source('last')

        # Then we perform autoprocessing
        fd = self._autoprocess(fd)

        #end of loading
        self._loading = False
        self.fd = fd

        # now we can plot
        self.can_plot = True

    def _performs_options(self):
        """Open the preference manager .

        """
        edit_options()

    def _performs_show_about(self):
        """ Display a view information: 'about Masai'

        """
        about_view = View(
                      Item( 'license',
                            show_label = False,
                            editor = ImageEditor(
                                    image = ImageResource( 'images/splash' ) ) 
                           ),
                      Group(UItem('license', 
                                 editor=HTMLEditor(format_text=True),
                                 width = 793,
                                 height = 300,
                                ), 
                            label="License"),
                      Group(Label(contact_label), label="Contribute"),
                    #    Group(Label(credits_label), label="Credits"),
                        title=u"About Masa\u00EF", buttons=["OK"],
                    #    icon=frame_icon
                    )
        self.edit_traits(kind="livemodal", view=about_view)

    def _performs_show_help(self):
        """Open the help pages

        """
        self._open_help()
        
    def _browser_open(self, url):
        """Open a Browser to display the help pages
    
        """
        if sys.platform == 'darwin':
                os.system('open %s &' % url)
        else:
            import webbrowser
            if webbrowser._iscommand('firefox'):
                firefox = webbrowser.get('firefox')
                firefox._invoke(['-chrome', url], remote=False, autoraise=True)
            else:
                webbrowser.open(url, autoraise=1)
    
    def _open_help(self):
        """ Open the masai user manual index in a browser.
    
        """
        url = "http://fernandezc.github.com/masai/doc/html/index.html"
        auto_close_message("Opening help in web browser...")
        self._browser_open(url)
        
    #===========================================================================
    # view
    #===========================================================================
    def default_traits_view(self):
        """Return the main view, with a left side containing the 
        controllers, and the right side the spectral view

        """
        return View(
                    HSplit(
                          InstanceUItem('controllers', width=.33,),
                          InstanceUItem('viewplot', width=.66,),
                          show_border=True,
                          visible_when='fd and fd.is_loaded and not _loading',),
                    title="%s (%s-%s)" % (_TITLE_, _VERSION_, _REVISION_) ,
                    resizable=True,
                    x=0,
                    y=20,
                    height=self.height,
                    width=self.width,
                    menubar=self.menubar,
                    handler=MasaiGuiWindowHandler(),
                   )

    #===========================================================================
    # _close
    #===========================================================================
    def _close(self):
        """Close the application

        """
        # TODO: performs some cleaning before closing
        print "exiting "
        sys.exit()

    #===========================================================================
    # events
    #===========================================================================
    @on_trait_change('fd')
    def _fd_updated(self):
        """The source fd has been changed. Pass the change to the panel
        and reset the ViewPlot
        """  

        if self.fd.is_loaded:
            logger.debug("main: source fd has changed")
            self.viewplot = ViewPlot(fd=self.fd)
            self.controllers = Controllers(fd=self.fd, viewplot=self.viewplot)

    #===========================================================================
    # __init__: initialisation
    #===========================================================================
    def __init__(self, **traits): 
        """
        Initialisation and setup of MasaiGuiMainWindow.

        The program try to read the last opened file 
        or present a dialog to select a new dataset  

        """
        super(MasaiGuiMainWindow, self).__init__(**traits)

        if self.applicationpref.get('application.last_source_file'):
            # open the last opened file if possible
            fd = Source('last')
        else:
            # ask which file to open
            fd = Source()

        if not fd.is_loaded:
            logger.error("Cannot load these data or the cancel button"+\
                         " was pushed.... program stopped")
            sys.exit()  
            #FIXME: avoid exiting the application for such stupid reason
        
        fd = self._autoprocess(fd)

        #end of loading
        self._loading = False
        self.fd = fd

        # now we can plot
        self.can_plot = True

    def _autoprocess(self, fd): 

        if eval(self.applicationpref.get('processing.process_automatically',
                                         'False')):
            # Fourier transform
            # but before we need to read the parameters 
            # from the source preference file 
            fd.TDeff[-1] = int(fd.sourcepref.get('processing.tdeff',
                                                 fd.TD[-1]))
            fd.SI[-1] = int(fd.sourcepref.get('processing.si',
                                            largest_power_of_2(fd.TD[-1]) * 2))
            fd.LB[-1] = float(fd.sourcepref.get('processing.lb', fd.LB[-1]))
            fd.PHC0[-1] = float(fd.sourcepref.get('processing.ph0',
                                                  fd.PHC0[-1])) % 360.0
            fd.PHC1[-1] = float(fd.sourcepref.get('processing.ph1',
                                                  fd.PHC1[-1]))
            fd.sourcepref.flush()

            efp(fd)

        return fd

#===============================================================================
# MasaiGuiWindowHandler
#===============================================================================
class MasaiGuiWindowHandler(Handler):
    """Handler for the guiwindow window: Essentially handle the exit process of the
    masai application

    """
    def close(self, info, _dummy=False):
        """Close the application after displaying a confirmation dialog
        
        """
        if info.initialized:
            retval = confirm(parent=info.ui.control,
                             message=u"Do you want to quit Masa\u00EF " + \
                             "(note: the current state is already saved)?",
                             title=u"Quit Masa\u00EF?",
                             default=YES)
            if retval == YES:
                info.object.controllers.fitcontroller.paramscript.timer.stop()
                info.object._close()
        return False

#===============================================================================
# run
#===============================================================================
def run():
    """Main entry to run the application
    
    """
    # TODO: Create a full pyface or envisage application
    # Create and open the main window.
    window = MasaiGuiMainWindow()

    time.sleep(5)
    _gui.start_event_loop() # A hack to close the splash screeen
    #TODO modify this ugly way to do it 
    #(use  a real pyface or envisage application)

    window.configure_traits()

   
#===============================================================================
if __name__ == "__main__":
    import cProfile
    print "OK"
    cProfile.run(
                 run()
                 )