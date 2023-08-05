.. include:: global.rst

.. _main:

####################################
Welcome to |masai|'s documentation!
####################################

:version: |version|

.. contents::
	:local:
	
What is |masai|?
================
|masai| is a software written in python and partially in fortran.

It (will) provides a framework for the processing, analysis and modelling of Solid State NMR spectra. It is cross platform, running on Linux, Windows and OS X.

A :ref:`gui` allows users to make basic processing and fitting of NMR spectra
(for now limited to the Bruker format).

The :ref:`api` should also be accessible to be included in other programs.

.. warning::

	|masai| is still experimental and under active development. 
	It is not mature nor stable. 
	Its current design is subject to major changes, reorganizations, bugs and crashes!!!.
	Should I say? be patient as I expect a fully working version with the upcoming 0.2 release.

Online Resources
==================

There are several online resources to help you get along with |masai|.

Issue tracker
--------------
    https://github.com/fernandezc/masai/issues

Source code repository
-----------------------
    https://github.com/fernandezc/masai

PyPI Entry
-----------
    http://pypi.python.org/pypi/masai/
    	
.. include:: citing.rst

.. _documentation:

Documentation map
======================

	.. toctree::
	   :maxdepth: 2
	   
	   install
	
	.. toctree::
	   :maxdepth: 2
	   
	   userguide
	
	.. toctree::
	   :maxdepth: 2
	   
	   develguide  
	      
	.. toctree::
	   :maxdepth: 1
	
	   faq
	   license

.. include:: changelog.rst
