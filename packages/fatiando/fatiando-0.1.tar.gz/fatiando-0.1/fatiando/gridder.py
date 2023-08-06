"""
Create and operate on grids and profiles.

**Grid generation**

* :func:`~fatiando.gridder.regular`
* :func:`~fatiando.gridder.scatter`

**Grid I/O**

**Grid operations**

* :func:`~fatiando.gridder.cut`
* :func:`~fatiando.gridder.interp`

**Misc**

* :func:`~fatiando.gridder.spacing`

----

"""

import numpy
import matplotlib.mlab

import fatiando.logger


log = fatiando.logger.dummy('fatiando.gridder')

def regular(area, shape, z=None):
    """
    Create a regular grid. Order of the output grid is x varies first, then y.

    Parameters:

    * area
        ``(x1, x2, y1, y2)``: Borders of the grid
    * shape
        Shape of the regular grid, ie ``(ny, nx)``.
    * z
        Optional. z coordinate of the grid points. If given, will return an
        array with the value *z*.

    Returns:

    * ``[xcoords, ycoords]``
        Numpy arrays with the x and y coordinates of the grid points
    * ``[xcoords, ycoords, zcoords]``
        If *z* given. Numpy arrays with the x, y, and z coordinates of the grid
        points

    """
    log.info("Generating regular grid:")
    ny, nx = shape
    x1, x2, y1, y2 = area
    dy, dx = spacing(area, shape)
    log.info("  area = (x1, x2, y1, y2) = %s" % (str((x1,x2,y1,y2))))
    log.info("  shape = (ny, nx) = %s" % (str(shape)))
    log.info("  spacing = (dy, dx) = %s" % (str((dy, dx))))
    log.info("  points = nx*ny = %d" % (nx*ny))
    x_range = numpy.arange(x1, x2, dx)
    y_range = numpy.arange(y1, y2, dy)
    # Need to make sure that the number of points in the grid is correct because
    # of rounding errors in arange. Sometimes x2 and y2 are included, sometimes
    # not
    if len(x_range) < nx:
        x_range = numpy.append(x_range, x2)
    if len(y_range) < ny:
        y_range = numpy.append(y_range, y2)
    assert len(x_range) == nx, "Failed! x_range doesn't have nx points"
    assert len(y_range) == ny, "Failed! y_range doesn't have ny points"
    xcoords, ycoords = [mat.ravel() for mat in numpy.meshgrid(x_range, y_range)]
    if z is not None:
        log.info("  z = %s" % (str(z)))
        zcoords = z*numpy.ones_like(xcoords)
        return [xcoords, ycoords, zcoords]
    else:
        return [xcoords, ycoords]

def scatter(area, n, z=None):
    """
    Create an irregular grid with a random scattering of points.

    Parameters:

    * area
        ``(x1, x2, y1, y2)``: Borders of the grid
    * n
        Number of points
    * z
        Optional. z coordinate of the points. If given, will return an
        array with the value *z*.

    Returns:

    * ``[xcoords, ycoords]``
        Numpy arrays with the x and y coordinates of the points
    * ``[xcoords, ycoords, zcoords]``
        If *z* given. Arrays with the x, y, and z coordinates of the points

    """
    x1, x2, y1, y2 = area
    log.info("Generating irregular grid (scatter):")
    log.info("  area = (x1, x2, y1, y2) = %s" % (str((x1,x2,y1,y2))))
    log.info("  number of points = n = %s" % (str(n)))
    xcoords = numpy.random.uniform(x1, x2, n)
    ycoords = numpy.random.uniform(y1, y2, n)
    if z is not None:
        log.info("  z = %s" % (str(z)))
        zcoords = z*numpy.ones(n)
        return [xcoords, ycoords, zcoords]
    else:
        return [xcoords, ycoords]

def spacing(area, shape):
    """
    Returns the spacing between grid nodes

    Parameters:

    * area
        ``(x1, x2, y1, y2)``: Borders of the grid
    * shape
        Shape of the regular grid, ie ``(ny, nx)``.

    Returns:

    * ``[dy, dx]``
        Spacing the y and x directions

    """
    x1, x2, y1, y2 = area
    ny, nx = shape
    dx = float(x2 - x1)/float(nx - 1)
    dy = float(y2 - y1)/float(ny - 1)
    return [dy, dx]

def interp(x, y, v, shape, area=None, algorithm='nn'):
    """
    Interpolate data onto a regular grid.

    .. warning:: Doesn't extrapolate. Will return a masked array in the 
        extrapolated areas.

    Parameters:

    * x, y : 1D arrays
        Arrays with the x and y coordinates of the data points.
    * v : 1D array
        Array with the scalar value assigned to the data points.
    * shape : tuple = (ny, nx)
        Shape of the interpolated regular grid, ie (ny, nx).
    * area : tuple = (x1, x2, y1, y2)
        The are where the data will be interpolated. If None, then will get the
        area from *x* and *y*.
    * algorithm : string
        Interpolation algorithm. Either ``'nn'`` for natural neighbor 
        or ``'linear'`` for linear interpolation. (see numpy.griddata)

    Returns:

    * ``[X, Y, V]``
        Three 2D arrays with the interpolated x, y, and v

    """
    if algorithm != 'nn' and algorithm != 'linear':
        raise ValueError("Invalid interpolation: %s" % (str(algorithm)))
    ny, nx = shape
    if area is None:
        area = (x.min(), x.max(), y.min(), y.max())
    x1, x2, y1, y2 = area
    xs = numpy.linspace(x1, x2, nx)
    ys = numpy.linspace(y1, y2, ny)
    X, Y = numpy.meshgrid(xs, ys)
    V = matplotlib.mlab.griddata(x, y, v, X, Y, algorithm)
    return [X, Y, V]

def cut(x, y, scalars, area):
    """
    Remove a subsection of the grid.

    Parameters:

    * x, y
        Arrays with the x and y coordinates of the data points.
    * scalars
        List of arrays with the scalar values assigned to the grid points.
    * area
        ``(x1, x2, y1, y2)``: Borders of the subsection

    Returns:

    * ``[subx, suby, subscalars]``
        Arrays with x and y coordinates and scalar values of the subsection.

    """
    xmin, xmax, ymin, ymax = area
    inside = []
    for i, coords in enumerate(zip(x, y)):
        xp, yp = coords
        if xp >= xmin and xp <= xmax and yp >= ymin and yp <= ymax:
            inside.append(i)
    subx = numpy.array([x[i] for i in inside])
    suby = numpy.array([y[i] for i in inside])
    subscalars = [numpy.array([scl[i] for i in inside]) for scl in scalars]
    return [subx, suby, subscalars]
