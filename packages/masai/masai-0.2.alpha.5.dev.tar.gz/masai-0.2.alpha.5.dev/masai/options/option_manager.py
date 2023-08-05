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
from traits.api import Color, Str, Float, Bool, List
from traitsui.api import View, Item, Group, VGroup, spring, SetEditor

#===============================================================================
# python imports
#===============================================================================
import os
import logging
logger = logging.getLogger()

#===============================================================================
# Local imports.
#===============================================================================
from apptools.preferences.api import Preferences
from apptools.preferences.api import get_default_preferences
from apptools.preferences.api import set_default_preferences
from apptools.preferences.ui.api import PreferencesManager, PreferencesPage

__all__ = ['get_categories', 'get_option_names', 
           'get_option', 'set_option', 'edit_options',
           'acqu_required', 'proc_required']

# the the preference default file:
filename = os.path.join("~",".masai","masai.ini")
set_default_preferences(Preferences(filename=os.path.expanduser(filename)))

# some useful lists
acqu_required = ['DECIM','DSPFVS','GRPDLY','NUC1', 'TD', 'AQ_mod', 'SW_h', 'TE', 'SFO1']
proc_required = ['SF', 'SI', 'TDeff', 'PHC1', 'PHC0', 'LB', 'GB', 'BC_mod', 'MC2']
_acqu = ['TL', 'WBST', 'SPNAM24', 'FQ3LIST', 'DSPFVS', 'SPNAM25', 'TPOFFS', 
         'LOCKFLD', 'VALIST', 'SPNAM31', 'SPNAM30', 'EXP', 'O8', 'DPNAME0', 
         'DPNAME1', 'DPNAME2', 'DPNAME3', 'DPNAME4', 'DPNAME5', 'DPNAME6', 
         'DPNAME7', 'LOCKPPM', 'SPNAM29', 'FQ7LIST', 'FQ1LIST', 'RPUUSED', 
         'GPNAM29', 'PRGAIN', 'SUBNAM3', 'BF3', 'BF2', 'BF1', 'RG', 'BF7', 
         'BF6', 'BF5', 'BF4', 'SPNAM9', 'BF8', 'NUC4', 'GPNAM17', 'GPNAM16', 
         'GPNAM15', 'GPNAM14', 'GPNAM13', 'D', 'GPNAM11', 'GPNAM10', 'LOCKPOW', 
         'TP', 'SUBNAM2', 'L', 'GPNAM19', 'GPNAM18', 'SPNAM22', 'P', 'SPNAM20', 
         'SPNAM21', 'GPX', 'GPY', 'GPZ', 'FCUCHAN', 'LGAIN', 'SOLVENT', 
         'SPNAM28', 'NUC1', 'TD', 'GP031', 'SUBNAM4', 'DBL', 'FQ2LIST', 
         'SUBNAM5', 'TPNAME2', 'DECBNUC', 'HGAIN', 'TPNAME5', 'TPNAME6', 
         'CHEMSTR', 'LOCKGN', 'CFRGTYP', 'RSEL', 'TPNAME1', 'DBP', 'GRDPROG', 
         'FnMODE', 'XGAIN', 'PH_ref', 'CNST', 'PARMODE', 'FQ6LIST', 
         'TPNAME4', 'DECIM', 'HL3', 'HL2', 'HL1', 'HPMOD', 'FTLPGN', 
         'ZGOPTNS', 'O6', 'TPNAME7', 'O5', 'PAPS', 'DP07', 'PR', 'DIGTYP',
         'NUC8', 'O4', 'DSLIST', 'ROUTWD2', 'O3', 'PROBHD', 'BYTORDA', 'AUNM', 
         'HDDUTY', 'O2', 'WBSW', 'O1', 'AMP', 'PL', 'USERA2', 'GPNAM31', 
         'GPNAM30', 'FOV', 'SPNAM3', 'LOCPHAS', 'WS', 'SPNAM6', 'DSPFIRM', 
         'DECNUC', 'GPNAM6', 'GPNAM5', 'GPNAM4', 'GPNAM3', 'F2LIST', 'GPNAM1', 
         'GPNAM0', 'FQ8LIST', 'GPNAM8', 'GPNAM7', 'PHP', 'LOCKED', 
         'TP07', 'FL1', 'FL3', 'FL2', 'DBPOAL', 'FL4', 'PROSOL', 'ZL4', 
         'NUCLEUS', 'INP', 'ZL3', 'V9', 'DBPNAM5', 'DBPNAM4', 'DBPNAM7', 
         'DBPNAM6', 'DBPNAM1', 'DBPNAM0', 'DBPNAM3', 'DBPNAM2', 'ROUTWD1', 
         'TUNXOUT', 'FS', 'HL4', 'GPNAM28', 'FW', 'GPNAM26', 'GPNAM27', 
         'GPNAM24', 'GPNAM25', 'GPNAM22', 'GPNAM23', 'GPNAM20', 'GPNAM21', 
         'SPNAM23', 'RECPH', 'TPOAL', 'TD0', 'HOLDER', 'SPOAL', 'YL', 'S', 
         'RD', 'FQ4LIST', 'RECCHAN', 'SPNAM2', 'DBP07', 'NC', 'VDLIST', 
         'SPNAM1', 'TEG', 'PULPROG', 'SPNAM0', 'GPNAM9', 
         'NBL', 'NUC5', 'DPOAL', 'NS', 'MASRLST', 'SPNAM7', 'MASR', 'DE', 
         'SPNAM5', 'XL', 'SFO3', 'SPNAM4', 'SPOFFS', 'OBSCHAN', 'INSTRUM', 
         'ZL1', 'NUC2', 'TE2', 'TE3', 'PRECHAN', 'SUBNAM0', 'SEOUT', 'RO', 
         'QNP', 'AQ_mod', 'SUBNAM7', 'SUBNAM6', 'SUBNAM9', 'SUBNAM8', 'AUTOPOS', 
         'SP', 'SW', 'SP07', 'PHCOR', 'TUNHIN', 'NUC3', 'SPECTR', 'SFO8', 
         'POWMOD', 'SPNAM8', 'DL', 'HPPRGN', 'NUC7', 'O7', 'CPDPRG8', 
         'CPDPRG7', 'CPDPRG6', 'CPDPRG5', 'CPDPRG4', 'CPDPRG3', 'CPDPRG2', 
         'CPDPRG1', 'F3LIST', 'DIGMOD', 'SW_h', 'LFILTER', 'DATE', 'HDRATE', 
         'PCPD', 'DPOFFS', 'DS', 'DP', 'GPNAM12', 'USERA1', 'LOCNUC', 'SPNAM18',
         'USERA4', 'USERA5', 'SPNAM13', 'DR', 'SPNAM11', 'SPNAM10', 'SPNAM17', 
         'SPNAM16', 'SPNAM15', 'SPNAM14', 'F1LIST', 'GPNAM2', 'DQDMODE', 
         'DECSTAT', 'LOCSHFT', 'TE', 'VTLIST', 'VPLIST', 'TPNAME3', 
         'FQ5LIST', 'VD', 'YMIN_a', 'OVERFLW', 'ZL2', 'SPNAM19', 
         'TPNAME0', 'LTIME', 'USERA3', 'TUNHOUT', 'IN', 'NUCLEI', 'PW', 
         'SFO2', 'QSB', 'QS', 'SFO1', 'SFO6', 'SFO7', 'SFO4', 'SFO5', 
         'CFDGTYP', 'AQSEQ', 'CPDPRGT', 'DTYPA', 'CPDPRG', 'DBPOFFS', 
         'SUBNAM1', 'YMAX_a', 'SWIBOX', 'NUC6', 'SPNAM12', 'SPNAM26', 
         'VCLIST', 'CPDPRGB', 'SPNAM27']
_acqu.sort()
for value in acqu_required:
    try:
        _acqu.remove(value)
    except:
        try: 
            logger.debug("%s not found"%value)
        except: 
            print"%s not found"%value
            
_proc = ['BCFW', 'ME_mod', 'WDW', 'STSR', 'STSI', 'PHC1', 'PHC0', 'PSIGN', 
         'COROFFS', 'YMAX_p', 'NCOEF', 'TI', 'GAMMA', 'INTBC', 'GB', 'PPRESOL', 
         'TDeff', 'NC_proc', 'AUNMP', 'F2P', 'PSCAL', 'AXTYPE', 'AXUNIT', 
         'PPARMOD', 'INTSCL', 'REVERSE', 'PH_mod', 'DFILT', 'PPDIAG', 'PPMPNUM', 
         'NOISF1', 'ASSWID', 'AXNUC', 'ASSFAC', 'PYNMP', 'TILT', 'SI', 'YMIN_p', 
         'PC', 'F1P', 'BYTORDP', 'SYMM', 'FTSIZE', 'OFFSET', 'DATMOD',  
         'ISEN', 'T1D', 'FCOR', 'MI', 'SF', 'TDoff', 'SPECTYP', 'SSB', 'AXRIGHT', 
         'AXNAME', 'XDIM', 'TOPLEV', 'ABSF2', 'ABSF1', 'NTH_PF', 'NTH_PI', 
         'FT_mod', 'ABSG', 'ABSL', 'AXLEFT', 'CY', 'TM1', 'TM2', 
         'S_DEV', 'SIOLD', 'LPBIN', 'SW_p', 'DC', 'SINO', 'USERP5', 'USERP4', 
         'USERP3', 'MC2', 'USERP1', 'NOISF2', 'LB', 'AZFE', 'LEV0', 'USERP2', 
         'AZFW', 'PKNL', 'NLEV', 'NSP', 'SIGF1', 'SIGF2', 'MEAN', 'NZP', 
         'BC_mod', 'AQORDER', 'PPIPTYP', 'ASSFACX', 'SREGLST', 'MAXI', 
         'ALPHA', 'ASSFACI', 'DTYPP']
_proc.sort()
for value in proc_required:
    try:
        _proc.remove(value)
    except:
        try: 
            logger.error("%s not found"%value)
        except: 
            print"%s not found"%value

#===============================================================================
# MasaiOptionPages()
#===============================================================================
class MasaiAppOptionPage(PreferencesPage):
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
# MasaiProcOptionPage
#===============================================================================
class MasaiProcOptionPage(PreferencesPage):
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
# MasaiPlotOptionPage
#===============================================================================
class MasaiPlotOptionPage(PreferencesPage):
    """ A preference page for the Masai workbench preferences. 
    """

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

#===============================================================================
# MasaiParamOptionPage
#===============================================================================
class MasaiParamOptionPage(PreferencesPage):
    """ A preference page for the Masai workbench preferences. 
    """

    #### 'IPreferencesPage' interface #########################################

    # The page's category (e.g. 'General/Appearence'). The empty string means
    # that this is a top-level page.
    category = ''

    # The page's help identifier (optional). If a help Id *is* provided then
    # there will be a 'Help' button shown on the preference page.
    help_id = ''

    # The page name (this is what is shown in the preferences dialog.
    name = 'Parameters'

    # The path to the preferences node that contains our preferences.
    preferences_path = 'parameters'

    #### Preferences ##########################################################

    acqu_selected = List( editor = SetEditor(
                values = _acqu,
                left_column_title  = 'Available Parameters',
                right_column_title = 'Selected Parameters' ) )

    proc_selected = List( editor = SetEditor(
                values = _proc,
                left_column_title  = 'Available Parameters',
                right_column_title = 'Selected Parameters' ) )


    #### Traits UI views ######################################################

    
    view = View(
        Group(
                Item( 'acqu_selected', style = 'simple' ),
                label       = 'Acquisition Parameters',
                show_labels = False,
                help = 'selection'
            ),
        Group(
                Item( 'proc_selected', style = 'simple' ),
                label       = 'Processing Parameters',
                show_labels = False,
            ),
        title   = 'Parameters',
    )
    
def get_categories():
    """Return a list of option categories for the application
    
    Examples
    --------
    >>> get_categories()
    ['application', 'processing', 'root', 'parameters', 'plot']
    
    """
    return get_default_preferences().node_names()

def get_option_names(category=None):
    """Get list of option names for a given category.
    
    Parameters
    ----------
    category : string
        The category to look for.
        
    Examples
    --------

    >>> from masai.api import get_option_names
    >>> get_option_names('application')    
    ['last_source_file', 'path_of_data', 'width', 'height']
    
    """
    if not category:
        return get_default_preferences().dump()
    
    return get_default_preferences().node(category).keys()

def get_option(category, option):
    """Get the value of a given option
    
    Parameters
    ----------
    category : string
        The category of preference
    option : string
        The option to get
        
    Examples
    --------

    >>> from masai.api import get_option
    >>> get_option('application','path_of_data') 
    '/users/christian/bruker/Data'
    
    """
    
    pref = get_default_preferences()
    return pref.get("%s.%s"%(category,option))
    
    

def set_option(category, option, value):
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

    >>> from masai.api import set_option
    >>> set_option('application','path_of_data','/users/christian/bruker/Data')    
    
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
            MasaiAppOptionPage(), 
            MasaiProcOptionPage(), 
            MasaiPlotOptionPage(),
            MasaiParamOptionPage()
        ]
    )

    # Show the UI...
    option_manager.configure_traits()

    # Save the preferences...
    get_default_preferences().flush()
    
# Entry point.
if __name__ == '__main__':

    #logger.addHandler(logging.StreamHandler())
    #logger.setLevel(logging.DEBUG)

    ## test
    #from masai.api import edit_options
    #edit_options()

    
    import nose
    nose.main()

    
#### EOF ######################################################################
