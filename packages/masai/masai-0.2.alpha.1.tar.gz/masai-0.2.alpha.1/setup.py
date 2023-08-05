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
This module is used to setup the application. Should work on all platform

The fortran part is compiled using numpy.distutils and numpy.f2py

"""
import sys
from setuptools import find_packages
from numpy.distutils.core import setup  

from masai.version import _VERSION_, _REVISION_, _TITLE_

with open('README.rst') as fp:
    LONG_DESCRIPTION = fp.read()

with open('doc/source/changelog.rst') as fp:
    LONG_DESCRIPTION += '\n\n' + fp.read()

DISTNAME = 'masai'
VERSION = "%s.%s" % (_VERSION_, _REVISION_)
DESCRIPTION = _TITLE_
AUTHOR = 'Christian Fernandez'
EMAIL = 'christian.fernandez@ensicaen.fr'
URL = 'http://fernandezc.github.com/masai'
DOWNLOADURL = 'http://pypi.python.org/pypi/masai/'
LICENSE = 'CeCILL-B'

CLASSIFIERS = [
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Science/Research',
        'Intended Audience :: Developers',
        'Intended Audience :: End Users/Desktop',
        'License :: Other/Proprietary License',
        'Programming Language :: Python',
        'Programming Language :: Fortran',
        'Topic :: Scientific/Engineering',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX :: Linux'
        ]    

mainscript = 'masai/masaigui.py'

if sys.platform == 'darwin':
    # This is not working on my machine... error with pyface?
    extra_options = dict(
                            setup_requires=['py2app'],
                            app=[mainscript],
                            options=dict(py2app=dict(argv_emulation=True,
                                 iconfile='masai/images/masai.icns',
                                 plist=dict(
                                         CFBundleIdentifier='org.masai.py2app',
                                         CFBundleGetInfoString =  _TITLE_,
                                        ),
                                 includes = [
                                        # The backends are dynamically imported and thus we need to
                                        # tell py2app about them.
                                        'kiva.*',
                                        'enable.*',
                                        'enable.wx.*',
                                        'pyface.*',
                                        'pyface.ui.wx.*',
                                        'pyface.ui.wx.action.*',
                                        'pyface.ui.wx.timer.*',
                                        'pyface.ui.wx.wizard.*',
                                        'pyface.ui.wx.workbench.*',
                                        'traitsui.wx.*',
                                        'traitsui.wx.extra.*',
                                        ],

                                  ),
                                ),
                            )
elif sys.platform == 'win32':
    #TODO: and check .. not done yet
    extra_options = dict(
        setup_requires=['py2exe', ],
        app=[mainscript],
    )
else:
    extra_options = dict(
        # Normally unix-like platforms will use "setup.py install"
        # and install the main script as such
        setup_requires=[],
        scripts=[mainscript],
        
    )

def configuration(parent_package='', top_path='.'):
    from numpy.distutils.misc_util import Configuration
    pulsar_dir = 'masai/modelling/pulsar'
    config = Configuration(DISTNAME,
                           parent_package,
                           top_path,
                           namespace_packages=['masai'],
                           version=VERSION,
                           author=AUTHOR,
                           author_email=EMAIL,
                           description=DESCRIPTION,
                           license=LICENSE,
                           url=URL,
                           long_description=LONG_DESCRIPTION)
    config.add_data_dir(('modelling/script/','masai/modelling/script/'))
    config.add_data_dir(('images/','masai/images/'))
    config.add_extension('forpulsar',
                  sources=['%s/f90/forpulsar.f90' % pulsar_dir,
                  '%s/f90/forpulsar.pyf' % pulsar_dir],
                  f2py_options=['--quiet'],
                  )
    return config

setup(configuration=configuration,
      download_url=DOWNLOADURL,
      classifiers=CLASSIFIERS,
      keywords='NMR, Python, Fortran',
      packages=find_packages(),
      include_package_data=True,
      #install_requires=['numpy'],
      zip_safe=True,
      requires=['numpy', 'scipy', 'matplotlib', 'traits'],
      entry_points={
        'console_scripts': [
            "masai = masai.masaigui:run",
        ],
      },
      **extra_options
      )
