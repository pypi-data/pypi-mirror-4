"""
GravMag: Center of mass estimation using the first eigenvector of the gravity
gradient tensor (2 sources with expanding windows)
"""
from fatiando import logger, mesher, gridder, utils, gravmag
from fatiando.vis import mpl, myv

log = logger.get()
log.info(logger.header())
log.info(__doc__)

# Generate some synthetic data
prisms = [mesher.Prism(-2500,-500,-1000,1000,500,2500,{'density':1000}),
          mesher.Prism(500,2500,-1000,1000,500,2500,{'density':1000})]
shape = (100, 100)
area = (-5000, 5000, -5000, 5000)
xp, yp, zp = gridder.regular(area, shape, z=-150)
noise = 2
tensor = [utils.contaminate(gravmag.prism.gxx(xp, yp, zp, prisms), noise),
          utils.contaminate(gravmag.prism.gxy(xp, yp, zp, prisms), noise),
          utils.contaminate(gravmag.prism.gxz(xp, yp, zp, prisms), noise),
          utils.contaminate(gravmag.prism.gyy(xp, yp, zp, prisms), noise),
          utils.contaminate(gravmag.prism.gyz(xp, yp, zp, prisms), noise),
          utils.contaminate(gravmag.prism.gzz(xp, yp, zp, prisms), noise)]
# Get the eigenvectors from the tensor data
eigenvals, eigenvecs = gravmag.tensor.eigen(tensor)
# Plot the data
titles = ['gxx', 'gxy', 'gxz', 'gyy', 'gyz', 'gzz']
mpl.figure()
for i, title in enumerate(titles):
    mpl.subplot(3, 2, i + 1)
    mpl.title(title)
    mpl.axis('scaled')
    levels = mpl.contourf(yp, xp, tensor[i], shape, 10)
    mpl.contour(yp, xp, tensor[i], shape, levels)
    mpl.m2km()
mpl.show()

# Pick the centers of the expanding windows
# The number of final solutions will be the number of points picked
mpl.figure()
mpl.suptitle('Pick the centers of the expanding windows')
mpl.axis('scaled')
mpl.contourf(yp, xp, tensor[-1], shape, 50)
mpl.colorbar()
centers = mpl.pick_points(area, mpl.gca(), xy2ne=True)
cms = []
for center in centers:
    # Use the first eigenvector to estimate the center of mass
    cm, sigma = gravmag.tensor.center_of_mass(xp, yp, zp, eigenvecs[0],
        windows=100, wcenter=center)
    cms.append(cm)
    print "Sigma = %g" % (sigma)

# Plot the prism and the estimated center of mass
# It won't work well because we're using only a single window
myv.figure()
myv.points(cms, size=300.)
myv.prisms(prisms, prop='density', opacity=0.5)
axes = myv.axes(myv.outline(extent=[-5000, 5000, -5000, 5000, 0, 5000]))
myv.wall_bottom(axes.axes.bounds, opacity=0.2)
myv.wall_north(axes.axes.bounds)
myv.show()
