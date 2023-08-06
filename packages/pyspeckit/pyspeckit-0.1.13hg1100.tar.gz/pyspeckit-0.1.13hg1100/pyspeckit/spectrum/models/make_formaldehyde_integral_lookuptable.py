import pyspeckit 
import numpy as np
from pylab import *

GF = pyspeckit.spectrum.models.gaussfitter.gaussian_fitter()
FM = pyspeckit.spectrum.models.formaldehyde_model()

xarr = pyspeckit.spectrum.units.SpectroscopicAxis(linspace(-25,25,251),'km/s',reffreq=4.82965996e9,reffreq_units='Hz')
X = logspace(-2,1,300)
gsfs = np.array([(GF.onepeakgaussian(linspace(-25,25,251),0,1,0,wid).sum()*0.2,FM.formaldehyde(xarr,1,0,wid).sum()*xarr.cdelt()) for wid in X])
R = gsfs[:,1]/gsfs[:,0]
gtp1 = X>0.1
ltp1 = (X<0.1)*(X>0.02)


figure(1)
clf()
subplot(211)
loglog(X,R)
plot(X[ltp1],10**polyval( polyfit(log10(X[ltp1]),log10(R[ltp1]),5), log10(X[ltp1]) ))
plot(X[gtp1],10**polyval( polyfit(log10(X[gtp1]),log10(R[gtp1]),5), log10(X[gtp1]) ))
gca().set_ylim(1,2.5)
subplot(212)
plot(X[ltp1],(R[ltp1]-10**polyval( polyfit(log10(X[ltp1]),log10(R[ltp1]),5), log10(X[ltp1]) ))/R[ltp1])
plot(X[gtp1],(R[gtp1]-10**polyval( polyfit(log10(X[gtp1]),log10(R[gtp1]),5), log10(X[gtp1]) ))/R[gtp1])
print "'lt0.1_11': np.array([%s])" % (",".join(["%10f" % p for p in polyfit(log10(X[ltp1]),log10(R[ltp1]),5)] ))
print "'gt0.1_11': np.array([%s])" % (",".join(["%10f" % p for p in polyfit(log10(X[gtp1]),log10(R[gtp1]),5)] ))


xarr2 = pyspeckit.spectrum.units.SpectroscopicAxis(linspace(-25,25,251),'km/s',reffreq=14.48847881e9,reffreq_units='Hz')
gsfs2 = np.array([(GF.onepeakgaussian(linspace(-25,25,251),0,1,0,wid).sum()*0.2,FM.formaldehyde(xarr2,1,0,wid).sum()*xarr2.cdelt()) for wid in X])
R2 = gsfs2[:,1]/gsfs2[:,0]

figure(2)
clf()
subplot(211)
loglog(X,R2)
plot(X[ltp1],10**polyval( polyfit(log10(X[ltp1]),log10(R2[ltp1]),6), log10(X[ltp1]) ))
plot(X[gtp1],10**polyval( polyfit(log10(X[gtp1]),log10(R2[gtp1]),6), log10(X[gtp1]) ))
gca().set_ylim(1,2.5)
subplot(212)
plot(X[ltp1],(R2[ltp1]-10**polyval( polyfit(log10(X[ltp1]),log10(R2[ltp1]),6), log10(X[ltp1]) ))/R2[ltp1])
plot(X[gtp1],(R2[gtp1]-10**polyval( polyfit(log10(X[gtp1]),log10(R2[gtp1]),6), log10(X[gtp1]) ))/R2[gtp1])
print "'lt0.1_22': np.array([%s])" % (",".join(["%10f" % p for p in polyfit(log10(X[ltp1]),log10(R2[ltp1]),6)] ))
print "'gt0.1_22': np.array([%s])" % (",".join(["%10f" % p for p in polyfit(log10(X[gtp1]),log10(R2[gtp1]),6)] ))
draw()
