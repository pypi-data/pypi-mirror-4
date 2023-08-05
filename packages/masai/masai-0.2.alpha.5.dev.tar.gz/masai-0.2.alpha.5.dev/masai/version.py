#! /usr/bin/env python
#===============================================================================
# version
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
This module contains version information. It use git to get the last version and
revision number.

"""
import commands

def get_git_version():
    """Get the current version  of the local git repository using
    the 'git describe' shell command.
    """
    status,output = commands.getstatusoutput('git describe')
    if status==0:
        return output.split('-')
    else:
        return '0.1','','' 

_TITLE_= u'Masai, a framework for processing and modelling of solid state NMR spectra'
_COPYRIGHT_ = u"2012-2013, C.Fernandez @ LCS (ENSICAEN/University of Caen/CNRS)"

x = get_git_version()
_VERSION_, _REVISION_, _GITID_ = x
