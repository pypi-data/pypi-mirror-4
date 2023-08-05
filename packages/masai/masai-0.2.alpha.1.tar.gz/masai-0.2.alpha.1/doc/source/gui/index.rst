.. include:: ../global.rst

.. _gui:

###################################
The Graphical User Interface (GUI) 
###################################

The *GUI* is 

.. contents::
	:local:
	

Getting started
================

After installation of |masai| (see the :ref:`installation` for details), 
the program should be available from command line
in the terminal::

	$ python masaigui.py

Copyright information are then echoed to the terminal console, 
while the program is loading::

	Masai, a framework for processing and modelling of solid state NMR spectra
	version : 0.1-0
	(c) 2012, C.Fernandez @ LCS (ENSICAEN/University of Caen/CNRS)


When the |masai| program is executed the first time, a preference file is created.

The dialog box shown in the following figure is then fired, which let you 
choose a Bruker dataset. 

.. _opendialogfig:

.. image:: images/opendialog.png
   :scale: 80
   
.. todo::

	For now, the opened dataset has to be in the Bruker format.
	Converters will be provided soon to convert from other format (like Agilent, 
	or even simple ascii files towards the Bruker format).
	
What the program wants to open is a fid or ser file (time domain data). 
Transformations to frequency domain will be done in a following step.

The path of the opened dataset is saved automatically in the preference file, so
that next run of |masai| will open it by default.

.. seealso::

	 If for some reasons you need to access manually to the preference file, see
	 :ref:`faq_preference_file`. 
	 

The main window for the |masai| application should appear after the previous step
and should display the last opened dataset in the right side of the window. 

.. image :: images/mainwindow.png
   :scale: 40

The Models
==========

The View
==========

The Controllers
================