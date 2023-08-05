#! /usr/bin/env python
#===============================================================================
# options.preferences_manager
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

""" Masai preferences manager. """

#===============================================================================
# Enthought library imports.
#===============================================================================
from traits.api import Color, Str, Float, Bool
from traitsui.api import View, Item, Group, VGroup, spring
import os

#===============================================================================
# Local imports.
#===============================================================================
from apptools.preferences.api import Preferences
from apptools.preferences.api import get_default_preferences
from apptools.preferences.api import set_default_preferences
from apptools.preferences.ui.api import PreferencesManager, PreferencesPage

__all__ = ['get_categories', 'get_options_names', 
           'get_options', 'set_options', 'edit_options']

# Create a preferences collection from a file and make it the default root
# preferences node for all preferences helpers etc.
# we don't need this when running the program from main.py
filename = os.path.join("~",".masai","masai.ini")
set_default_preferences(Preferences(filename=os.path.expanduser(filename)))

#===============================================================================
# MasaiPreferencesPage
#===============================================================================
class MasaiAppPreferencesPage(PreferencesPage):
    """ A preference page for the Masai preferences. """

    #### 'IPreferencesPage' interface #########################################

    # The page's category (e.g. 'General/Appearence'). The empty string means
    # that this is a top-level page.
    category = ''

    # The page's help identifier (optional). If a help Id *is* provided then
    # there will be a 'Help' button shown on the preference page.
    help_id = ''

    # The page name (this is what is shown in the preferences dialog.
    name = 'Application'

    # The path to the preferences node that contains our preferences.
    preferences_path = 'application'
    
    #### Preferences ##########################################################

    last_source_file = Str('')
    path_of_data = Str( os.path.expanduser('~/bruker/Data'))
    width = Float(1.0)
    height = Float(0.9)
     
    #### Traits UI views ######################################################

    view = View(Group(
                    VGroup(
                           Item('last_source_file'), 
                           Item('path_of_data'),
                           label = 'Source paths',
                          ),
                    VGroup( 
                           Item('width'),
                           Item('height'),
                           spring,
                           label = 'main window',
                           ),
                    orientation = 'vertical',
                    ),
                )

#===============================================================================
# MasaiProcPreferencesPage
#===============================================================================
class MasaiProcPreferencesPage(PreferencesPage):
    """ A preference page for the Masai preferences. """

    #### 'IPreferencesPage' interface #########################################

    # The page's category (e.g. 'General/Appearence'). The empty string means
    # that this is a top-level page.
    category = ''

    # The page's help identifier (optional). If a help Id *is* provided then
    # there will be a 'Help' button shown on the preference page.
    help_id = ''

    # The page name (this is what is shown in the preferences dialog.
    name = 'Processing'

    # The path to the preferences node that contains our preferences.
    preferences_path = 'processing'
    
    #### Preferences ##########################################################

    process_automatically = Bool(True)
    
     
    #### Traits UI views ######################################################

    view = View('''process_automatically'''
                )

#===============================================================================
# MasaiFilesPreferencesPage
#===============================================================================
class MasaiPlotPreferencesPage(PreferencesPage):
    """ A preference page for the Masai workbench preferences. """

    #### 'IPreferencesPage' interface #########################################

    # The page's category (e.g. 'General/Appearence'). The empty string means
    # that this is a top-level page.
    category = ''

    # The page's help identifier (optional). If a help Id *is* provided then
    # there will be a 'Help' button shown on the preference page.
    help_id = ''

    # The page name (this is what is shown in the preferences dialog.
    name = 'Plot'

    # The path to the preferences node that contains our preferences.
    preferences_path = 'plot'

    #### Preferences ##########################################################

    bgcolor = Color('white')
    fgcolor = Color('black')

    #### Traits UI views ######################################################

    view = View('bgcolor', 'fgcolor')

def get_categories():
    """Return a list of option categories for the application
    
    Examples
    --------
    >>> get_categories()
    ['application', 'processing', 'root', 'plot']
    
    """
    return get_default_preferences().node_names()

def get_options_names(category=None):
    """Get list of option names for a given category.
    
    Parameters
    ----------
    category : string
        The category to look for.
        
    Examples
    --------

    >>> from masai.api import get_options
    >>> get_options_names('application')    
    ['last_source_file', 'path_of_data', 'width', 'height']
    
    """
    if not category:
        return get_default_preferences().dump()
    
    return get_default_preferences().node(category).keys()

def get_options(category, option):
    """Get the value of a given option
    
    Parameters
    ----------
    category : string
        The category of preference
    option : string
        The option to get
        
    Examples
    --------

    >>> from masai.api import set_options
    >>> get_options('application','path_of_data') 
    '/users/christian/bruker/Data'
    
    """
    
    pref = get_default_preferences()
    return pref.get("%s.%s"%(category,option))
    
    

def set_options(category, option, value):
    """Set a given option to some value
    
    Parameters
    ----------
    category : string
        The category of preference
    option : string
        The option to set
    value : any
        The value of the option to set
        
    Examples
    --------

    >>> from masai.api import set_options
    >>> set_options('application','path_of_data','/users/christian/bruker/Data')    
    
    """
    
    pref = get_default_preferences()
    pref.set("%s.%s"%(category,option),value)
    pref.flush()
    
def edit_options():
    """Open a view to manage the options/preference for the whole application
    
    Examples
    --------
   
    >>> from masai.api import edit_options
    >>> edit_options()

    """
    option_manager = PreferencesManager(
        pages = [
            MasaiAppPreferencesPage(), 
            MasaiProcPreferencesPage(), 
            MasaiPlotPreferencesPage()
        ]
    )

    # Show the UI...
    option_manager.configure_traits()

    # Save the preferences...
    get_default_preferences().flush()
    
# Entry point.
if __name__ == '__main__':

    import nose
    nose.main()

    
#### EOF ######################################################################
