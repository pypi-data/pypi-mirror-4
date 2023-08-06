"""
GravMag: 3D imaging using the Generalized Inverse method on synthetic gravity
data (simple model)
"""
from fatiando import logger, gridder, mesher, gravmag
from fatiando.vis import mpl, myv

log = logger.get()
log.info(logger.header())
log.info(__doc__)

# Make some synthetic gravity data from a simple prism model
prisms = [mesher.Prism(-1000,1000,-3000,3000,0,5000,{'density':1000})]
shape = (25, 25)
xp, yp, zp = gridder.regular((-5000, 5000, -5000, 5000), shape, z=-10)
gz = gravmag.prism.gz(xp, yp, zp, prisms)

# Plot the data
mpl.figure()
mpl.axis('scaled')
mpl.contourf(yp, xp, gz, shape, 30)
mpl.colorbar()
mpl.xlabel('East (km)')
mpl.ylabel('North (km)')
mpl.m2km()
mpl.show()

# Run the Generalized Inverse
mesh = gravmag.imaging.geninv(xp, yp, zp, gz, shape, 0, 10000, 25)

# Plot the results
myv.figure()
myv.prisms(prisms, 'density', style='wireframe', linewidth=5)
myv.prisms(mesh, 'density', edges=False)
axes = myv.axes(myv.outline())
myv.wall_bottom(axes.axes.bounds)
myv.wall_north(axes.axes.bounds)
myv.show()
