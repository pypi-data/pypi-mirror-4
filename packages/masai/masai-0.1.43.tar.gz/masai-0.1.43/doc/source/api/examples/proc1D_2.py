#$ proc_1D
import pylab as pl

# You must always import the needed function or classes
from masai.api import Source, efp, pk, apk
# or do a wild import using:
#from masai import Source, efp
# Uncomment the above line to use it.

# read the data and open a new instance of Source
spc = Source('test/1')
fig1 = pl.figure(1,figsize=(10,4))      # to create a figure

# make some processings
spc.LB[-1] = 50.         # set line broadening
efp(spc)                 # make em, ft and pk at once
# you can add an automatic phase correction of 
# the newly (not well phased) data
apk(spc)
# or phase it manually
spc.PHC0[-1] = 1.        # set the 0-order phase parameter in degrees
spc.PHC1[-1] = 0.        # set the 1-order phase parameter in degrees
pk(spc)                  # apply the phase

# now plot it
data = spc.data.real     # take only the real part
pl.plot(data, 'k')       # create a plot in fig1 with a black trace
pl.show()                # show the fig1              

