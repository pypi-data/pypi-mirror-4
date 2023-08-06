from pynfftls import *
import numpy as np
import matplotlib.pyplot as plt
import math

# sampling
dt=1.

# number of measurements
n = 100000

# sampling time
dt = 0.01

nu0 = 0.1

T = n*dt

# time series
t = np.arange(n)*dt -T/2.

Te = T *0.25
y = np.sin(math.pi*2.*nu0*t) * ( (t <= Te/2) & (t >= -Te/2) )

# we compute the NFFT:
p = n/2 # number of positive frequencies
(f,A) = nfft(t,y,p,dt=dt)

xm = math.pi*(nu0-f)* Te
xp = math.pi*(nu0+f)* Te


# calculation of the FFT:
B = np.fft.fft(y,n)
nu = np.fft.fftfreq(n,d=dt)
# The FFT assumes a times series in the interval [0,T]
# while the NFFT in the interval [-T/2,T/2[
# we apply on the FFT the appropriate phase term: 
B = B*np.exp(math.pi*1j*nu*T)

#C = np.fft.rfft(y,n)

# we compute the Direct FT for a limited frequency range:
j  = np.where(  ( (f < nu0*1.1) & (f > nu0*0.9))  | ( (f > -nu0*1.1) & (f < -nu0*0.9))  )
j = j[0]
C = dft(t,y,f[j])

# calculation of the analytic expression
D = np.zeros((2*p),dtype=np.cdouble)
for i in range(2*p):
    ixm = xm[i]
    ixp = xp[i]
    if( abs(ixm) > 1e-5 and abs(ixp)> 1e-5 ):
        D[i] =  -1j * 0.5  * Te * ( math.sin(ixm)/ixm  - math.sin(ixp)/ixp ) /dt
    elif (abs(ixm) <= 1e-5):
        D[i] =  -1j *0.5 *Te  * ( 1. - math.sin(ixp)/ixp )/dt
    elif (abs(ixp) <= 1e-5 ):
         D[i] =  -1j * 0.5 *Te  * ( - 1. + math.sin(ixm)/ixm ) /dt 
        
plt.figure(0)
plt.clf()
plt.plot(f,abs(A))
plt.plot(nu,abs(B))
plt.plot(f,abs(D))
plt.plot(f[j],abs(C),'o')
plt.axis([nu0*0.9,nu0*1.1,0,np.max(abs(A))])

plt.figure(1)
plt.clf()
plt.plot(f,np.imag(A))
plt.plot(nu,np.imag(B))
plt.plot(f,np.imag(D))
plt.plot(f[j],np.imag(C),'o')
plt.axis([nu0*0.9,nu0*1.1,np.min(np.imag(A)),np.max(np.imag(A))])

plt.show()
