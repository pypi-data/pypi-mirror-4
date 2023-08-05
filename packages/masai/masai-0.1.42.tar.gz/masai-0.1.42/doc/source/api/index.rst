.. include:: ../global.rst

.. _api:

############################################
The Application Programming Interface (API)
############################################

Some classes and function of **Masaï** are available to be used in other programs
or directly from a python shell.

Here we explain how to use the API in interactive or scripting mode.

.. contents::
	:local:
	
	
Getting started
===============

One of the simplex way to work with the api it is from a **IPython** shell.

Open IPython
------------

IPython is installed with the EPD distribution that is recommended to work with this project.

However, if you prefer you can also download it separately from 
`ipython.org <http://ipython.org/download.html>`_

When IPython is available, go to a terminal::

	$ ipython --pylab

The (optional) command argument `--pylab` is interesting as it automatically load the 
`matplotlib <http://matplotlib.org>`_ libraries (useful for plotting data).
	
You should get something like::

	Python 2.7.3 |EPD 7.3-2 (32-bit)| (default, Apr 12 2012, 11:28:34) 
	Type "copyright", "credits" or "license" for more information.
	
	IPython 0.12.1 -- An enhanced Interactive Python.
	?         -> Introduction and overview of IPython's features.
	%quickref -> Quick reference.
	help      -> Python's own help system.
	object?   -> Details about 'object', use 'object??' for extra details.
	
	Welcome to pylab, a matplotlib-based Python environment [backend: WXAgg].
	For more information, type 'help(pylab)'.

and then the IPython prompt, where you can type the suggested command:

.. sourcecode:: ipython

	In [1]: help(pylab) # will provide a list of the pylab commands 


One of the first recommended action is to set some preferences for the API such as the 
**default path** of the data. To do this , open the options/preferences manager (also
available in the :ref:`gui` application):

.. sourcecode:: ipython

	In [2]: from masai.api import edit_options
	
	In [3]: edit_options()


This path can also be set directly, e.g., you can do:

.. sourcecode:: ipython

	In [4]: from masai.api import set_options
	
	In [5]: set_options('application', 'path_of_data','/users/christian/Bruker/Data')
		
In the above command we assume that the path of the data is '/users/christian/Bruker/Data'
like in my computer, but you can of course use whatever you like which corresponds to your needs.

Using IPython, you can either use |masai| in interactive mode or by running scripts.

Interactive mode
----------------

In interactive mode, you execute the command in the IPython console (ala MATLAB!).

for instance, you can make a plot of some data. In this example, we use our test data that are shipped with the program (look in the *data/* directory):

.. sourcecode:: ipython

	In [6]: from masai.api import *   # so we import all possible function and variables from the API 
	
	In [7]: fid = Source('test/1')    # here we open an fid as an instance of the class Source
	
We can immediately check if the data are properly accessibles, and then plot the fid:

.. sourcecode:: ipython

	In [8]:  fid.data
	Out[8]: 
	array([ -4.34014773e-01 +5.17775109e-01j,
         	1.52203424e+00 -2.11576098e+00j,
         	2.60024037e+00 -4.15961950e+00j, ...,
         	6.24400476e-03 -1.18999032e-02j,
           -4.52527535e-03 +3.20101539e-04j,  -4.12848480e-04 -4.43371582e-03j]) 
	
	In [9]: plot(fid.data.real)
	Out[9]: [<matplotlib.lines.Line2D at 0x85e57d0>]	
	
A window is opened showing your plotted data.

.. image:: images/plot.*

You can refer to the documentation of `matplotlib <http://matplotlib.org>`_ (`pylab <http://matplotlib.org/faq/usage_faq.html>`_) to get advanced information
on how to manage such plots. 
 

How To Do?
==========

.. toctree::
	:maxdepth: 2
	
	apihowto		
	
