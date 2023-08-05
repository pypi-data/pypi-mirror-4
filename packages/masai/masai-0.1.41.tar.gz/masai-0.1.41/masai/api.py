# api
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

"""This module is the main API (Application Programming Interface).

Up to now, only the :ref:`Source <source>` class 
and the :ref:`processing functions <process>` 
are made available to the user.

exemple
-------

    >>> import masai.api
    >>> fd = Source('test/1')  # read the source dataset
    >>> efp(fd)                # performs EM+FT+PK (similar to Bruker commands)


"""

from masai.fileio.source import Source
from masai.options import *
from masai.processing.process import * 

