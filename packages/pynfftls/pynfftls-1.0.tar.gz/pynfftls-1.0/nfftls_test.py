from pynfftls import *
import numpy as np
import matplotlib.pyplot as plt
import math



# sampling
dt=1.

# number of measurements
n = 1000

# time series
t = np.arange(n)*dt

# total duration
duration = n*dt

# sinusoidal function + white noise:
nu0 = 1./10.
a0 = 0.5

hifac = 1.
ofac = 1.
sig = 1

y = np.random.randn((n))*sig + a0*np.cos(2.*math.pi * nu0 * t)   
    
(f,p) = period(t,y,ofac,hifac)

plt.clf()
plt.plot(f,p)
plt.loglog()

plt.show()

