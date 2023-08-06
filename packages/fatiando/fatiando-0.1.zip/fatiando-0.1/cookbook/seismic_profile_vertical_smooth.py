"""
Seismic: Invert vertical seismic profile (VSP) traveltimes using smoothness
regularization
"""
import numpy
from fatiando import logger, utils, seismic, vis

log = logger.get()
log.info(logger.header())
log.info(__doc__)

log.info("Generating synthetic data")
thickness = [10, 20, 10, 30, 40, 60]
velocity = [2000, 1000, 5000, 1000, 2500, 6000]
zp = numpy.arange(1., sum(thickness), 1., dtype='f')
tts, error = utils.contaminate(
    seismic.profile.vertical(thickness, velocity, zp),
    0.02, percent=True, return_stddev=True)

log.info("Preparing for the inversion using 5 m thick layers")
thick = 10.
mesh = [thick]*int(sum(thickness)/thick)
smooth = 50.
estimates = []
for i in xrange(30):
    p, r = seismic.profile.ivertical(utils.contaminate(tts, error), zp, mesh,
        smooth=smooth)
    estimates.append(1./p)
estimate = utils.vecmean(estimates)
predicted = seismic.profile.vertical(mesh, estimate, zp)

log.info("Plotting results...")
vis.mpl.figure(figsize=(12,5))
vis.mpl.subplot(1, 2, 1)
vis.mpl.grid()
vis.mpl.title("Vertical seismic profile")
vis.mpl.plot(tts, zp, 'ok', label='Observed')
vis.mpl.plot(predicted, zp, '-r', linewidth=3, label='Predicted')
vis.mpl.legend(loc='upper right', numpoints=1)
vis.mpl.xlabel("Travel-time (s)")
vis.mpl.ylabel("Z (m)")
vis.mpl.ylim(sum(thickness), 0)
vis.mpl.subplot(1, 2, 2)
vis.mpl.grid()
vis.mpl.title("True velocity + smooth estimate")
for p in estimates:
    vis.mpl.layers(mesh, p, '-r', linewidth=2, alpha=0.2)
vis.mpl.layers(mesh, estimate, '.-k', linewidth=2, label='Mean estimate')
vis.mpl.layers(thickness, velocity, '--b', linewidth=2, label='True')
vis.mpl.ylim(sum(thickness), 0)
vis.mpl.xlim(0, 10000)
vis.mpl.legend(loc='upper right', numpoints=1)
vis.mpl.xlabel("Velocity (m/s)")
vis.mpl.ylabel("Z (m)")
vis.mpl.show()
