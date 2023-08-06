"""
GravMag: Generate noise-corrupted gravity gradient tensor data
"""
from fatiando import logger, mesher, gridder, gravmag, utils
from fatiando.vis import mpl

log = logger.get()
log.info(logger.header())
log.info(__doc__)

prisms = [mesher.Prism(-1000,1000,-1000,1000,0,2000,{'density':1000})]
shape = (100,100)
xp, yp, zp = gridder.regular((-5000, 5000, -5000, 5000), shape, z=-200)
components = [gravmag.prism.gxx, gravmag.prism.gxy, gravmag.prism.gxz,
              gravmag.prism.gyy, gravmag.prism.gyz, gravmag.prism.gzz]
log.info("Calculate the tensor components and contaminate with 5 Eotvos noise")
ftg = [utils.contaminate(comp(xp, yp, zp, prisms), 5.0) for comp in components]

log.info("Plotting...")
mpl.figure(figsize=(14,6))
mpl.suptitle("Contaminated FTG data")
names = ['gxx', 'gxy', 'gxz', 'gyy', 'gyz', 'gzz']
for i, data in enumerate(ftg):
    mpl.subplot(2,3,i+1)
    mpl.title(names[i])
    mpl.axis('scaled')
    levels = mpl.contourf(xp*0.001, yp*0.001, data, (100,100), 12)
    mpl.colorbar()
    mpl.contour(xp*0.001, yp*0.001, data, shape, levels, clabel=False)
mpl.show()
