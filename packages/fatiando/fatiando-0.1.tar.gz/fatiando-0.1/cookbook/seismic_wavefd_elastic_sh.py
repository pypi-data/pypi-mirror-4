"""
Seismic: 2D finite difference simulation of elastic SH wave propagation
"""
import numpy as np
from matplotlib import animation
from fatiando import seismic, logger, gridder, vis

log = logger.get()

# Make a wave source from a mexican hat wavelet
sources = [seismic.wavefd.MexHatSource(25, 25, 100, 0.5, delay=1.5)]
# Set the parameters of the finite difference grid
shape = (100, 100)
spacing = (500, 500)
area = (0, spacing[1]*shape[1], 0, spacing[0]*shape[0])
# Make a density and S wave velocity model
dens = 2700*np.ones(shape)
svel = 3000*np.ones(shape)

# Get the iterator. This part only generates an iterator object. The actual
# computations take place at each iteration in the for loop bellow
dt = 0.05
maxit = 400
timesteps = seismic.wavefd.elastic_sh(spacing, shape, svel, dens, dt, maxit,
    sources, padding=0.5)

# This part makes an animation using matplotlibs animation API
vmin, vmax = -1*10**(-4), 1*10**(-4)
fig = vis.mpl.figure()
vis.mpl.axis('scaled')
x, z = gridder.regular(area, shape)
# Start with everything zero and grab the plot so that it can be updated later
wavefield = vis.mpl.pcolor(x, z, np.zeros(shape).ravel(), shape, vmin=vmin,
    vmax=vmax)
# Make z positive down
vis.mpl.ylim(area[-1], area[-2])
vis.mpl.m2km()
vis.mpl.xlabel("x (km)")
vis.mpl.ylabel("z (km)")
# This function updates the plot every few timesteps
steps_per_frame = 10
def animate(i):
    for t, u in enumerate(timesteps):
        if t == steps_per_frame - 1:
            vis.mpl.title('time: %0.1f s' % (i*steps_per_frame*dt))
            wavefield.set_array(u[0:-1,0:-1].ravel())
            break
    return wavefield,
anim = animation.FuncAnimation(fig, animate,
    frames=maxit/steps_per_frame, interval=1, blit=True)
#anim.save('sh_wave.mp4', fps=10)
vis.mpl.show()

