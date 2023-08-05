.. include:: global.rst

.. _installation:

###################
Installation Guide
###################

Where to get |masai| 
=====================

To get a working installation of |masai|, on any platform (windows, mac OS X, Linux ... ), 
several solutions are (or will be soon) available.

* :ref:`binaries`

* :ref:`pypi`
 
* :ref:`dev`

* :ref:`clone` 
   

Requirements
=============

|masai| requires a working python installation. 

* `Python <http://www.python.org/>`_ 

and a fortran90 compiler. If you do not have this on your computer, 
you can use for instance:

* `gfortran <http://gcc.gnu.org/wiki/GFortran>`_

Currently, only the python 2.7 version has been tested. It should work with
previous version of python, and (although not checked) should not worked with 
python 3.0.

The following libraries are also required:

* `Numpy <http://numpy.scipy.org>`_ 
    
* `Scipy <http://www.scipy.org/>`_
    
* `Matplotlib <http://matplotlib.sourceforge.net/index.html>`_

* `Traits <http://code.enthought.com/projects/traits/>`_
    
* `Pyface <http://code.enthought.com/projects/pyface/>`_
        
Follow the instructions to install these packages on those sites, or, far easier, 
install them as packages from your operating system 
(e.g. apt-get or the synaptic GUI on Ubuntu, `Macports <http://www.macports.org/>`_ on OS X, etc.).

Regarding the installation of all these above packages, we highy recommend to install EPD python framework (a much straitforward solution!) 
which is available for most platforms:

* `Enthougth Python Distribution (EPD) <http://www.enthought.com/products/epd.php>`_ 

Finally, it is recommended to use the `pip`_ 
installer for a really easy installation of |masai| from the Pypi repository. To install 
`pip`_ for the first time, you need to execute::

$ easy_install pip 

on a terminal. 

`easy_install`_ is in principle already present in you EPD python installation.

Installation
=============

.. _binaries:

Installation from binaries
***************************

.. todo::

	Not yet available, sorry. 

.. _pypi:

Standard installation from PyPi sources
*****************************************

Very simple, use the following command in a terminal::

$ pip install masai

or to update a previous installation with the latest stable release::

$ pip install -U masai

.. _dev:

Installation from developpement sources
******************************************************

.. warning::

	These sources may be unstable or even broken.
	 
Downloads zip/tar archives working for all platforms are available.
You can use the following links after having read the License information 
(`LICENSE (en) <_static/Licence_CeCILL-B_V1-en.html>`_ 
or `LICENCE (fr) <_static/Licence_CeCILL-B_V1-fr.html>`_)

* `tar archives <https://github.com/fernandezc/masai/tarball/master>`_

* `zip archives <https://github.com/fernandezc/masai/zipball/master>`_

or on PyPi:

* `Download tar.gz archives from PyPi <http://pypi.python.org/pypi/masai>`_

Ungzip and untar the source package, cd to the new directory, and execute::

	$ python setup.py install

or better ::

	$ python setup.py develop 
	
to install it in the developper mode.

.. tip::

	On most UNIX-like systems, you’ll probably need to run these commands as root or using sudo.

.. _clone:

Clone or fork of the Github repository
***************************************
Alternatively, you can make a clone/fork of the github sources at: 

* `https://github.com/fernandezc/masai  <https://github.com/fernandezc/masai>`_

This is the recommended solution for developpers 
and those who would like to contribute


Check the installation
=======================

The simplest way, if to check the correct installation of the `GUI` application.
Type in a terminal::

$ masai

and the main window of the application should appear after some initializations
(few seconds).

Alternatively, to check the `API`, you should also be able to 
get the following import working correctly in a python session or better in IPython console.

Run a IPython session by issuing in the terminal the following command::

	$ ipython
	
Then execute two commands as following:
	
.. sourcecode:: ipython

    In [1]: from masai.api import Source
    
    In [2]: fd = Source()
    
where the second commands should open a dialog to set the current dataset source.

If this goes well, the |masai| application is properly installed.



.. _`easy_install`: http://pypi.python.org/pypi/setuptools
.. _`pip`: http://pypi.python.org/pypi/pip