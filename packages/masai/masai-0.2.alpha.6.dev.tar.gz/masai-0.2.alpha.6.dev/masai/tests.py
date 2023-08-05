#! /usr/bin/env python
#===============================================================================
# tests
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
This module execute `nose <https://nose.readthedocs.org/en/latest/>`_ testing 
for the whole application (including docstrings). Can be run from the terminal::

    $ python tests.py
    
Alternatively, same results can be obtained using::

    $ nosetests

"""
if __name__ == '__main__':

    import nose
    nose.main()
