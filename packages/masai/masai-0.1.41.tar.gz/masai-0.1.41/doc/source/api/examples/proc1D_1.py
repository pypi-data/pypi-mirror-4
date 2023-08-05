#$ proc_1D

from masai.api import Source
import pylab as pl

# read the data and open a new instance of Source

spc = Source('test/1')
fig1 = pl.figure(1, figsize=(10,3))      # to create a figure
data = spc.data.real     # take only the real part
pl.plot(data, 'k')       # create a plot in fig1 with a black trace
data = spc.data.imag     # take now the imaginary part
pl.plot(data, 'r')       # add it to the plot with a red trace
pl.xlim(0, 300)          # shows only the first 300 points
pl.show()                # show the fig1              
