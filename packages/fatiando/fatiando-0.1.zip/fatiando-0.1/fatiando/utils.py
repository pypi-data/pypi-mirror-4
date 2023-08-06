"""
Miscellaneous utility functions and classes.

**Mathematical functions**

* :func:`~fatiando.utils.normal`
* :func:`~fatiando.utils.gaussian`
* :func:`~fatiando.utils.gaussian2d`

**Point scatter generation**

* :func:`~fatiando.utils.random_points`
* :func:`~fatiando.utils.circular_points`
* :func:`~fatiando.utils.connect_points`

**Unit conversion**

* :func:`~fatiando.utils.si2mgal`
* :func:`~fatiando.utils.mgal2si`
* :func:`~fatiando.utils.si2eotvos`
* :func:`~fatiando.utils.eotvos2si`
* :func:`~fatiando.utils.si2nt`
* :func:`~fatiando.utils.nt2si`

**Coordinate system conversions**

* :func:`~fatiando.utils.sph2cart`

**Others**

* :func:`~fatiando.utils.contaminate`: Contaminate a vector with pseudo-random
  Gaussian noise
* :func:`~fatiando.utils.dircos`: Get the 3 coordinates of a unit vector
* :func:`~fatiando.utils.vecmean`: Take the mean array out of a list of arrays
* :func:`~fatiando.utils.vecstd` Take the standard deviation array out of a list
  of arrays
* :class:`~fatiando.utils.SparseList`: Store only non-zero elements on an
  immutable list
* :func:`~fatiando.utils.sec2hms`: Convert seconds to hours, minutes, and
  seconds
* :func:`~fatiando.utils.sec2year`: Convert seconds to Julian years
* :func:`~fatiando.utils.year2sec`: Convert Julian years to seconds

----

"""

import math

import numpy

import fatiando.constants
import fatiando.logger

log = fatiando.logger.dummy('fatiando.utils')


def sph2cart(lon, lat, height):
    """
    Convert spherical coordinates to Cartesian geocentric coordinates.

    Parameters:

    * lon, lat, height : floats
        Spherical coordinates. lon and lat in degrees, height in meters. height
        is the height above mean Earth radius.

    Returns:

    * x, y, z : floats
        Converted Cartesian coordinates

    """
    d2r = numpy.pi/180.0
    radius = fatiando.constants.MEAN_EARTH_RADIUS + height
    x = numpy.cos(d2r*lat)*numpy.cos(d2r*lon)*radius
    y = numpy.cos(d2r*lat)*numpy.sin(d2r*lon)*radius
    z = numpy.sin(d2r*lat)*radius
    return x, y, z

def si2nt(value):
    """
    Convert a value from SI units to nanoTesla.

    Parameters:

    * value : number or array
        The value in SI

    Returns:

    * value : number or array
        The value in nanoTesla

    """
    return value*fatiando.constants.T2NT

def nt2si(value):
    """
    Convert a value from nanoTesla to SI units.

    Parameters:

    * value : number or array
        The value in nanoTesla

    Returns:

    * value : number or array
        The value in SI

    """
    return value/fatiando.constants.T2NT

def si2eotvos(value):
    """
    Convert a value from SI units to Eotvos.

    Parameters:

    * value : number or array
        The value in SI

    Returns:

    * value : number or array
        The value in Eotvos

    """
    return value*fatiando.constants.SI2EOTVOS

def eotvos2si(value):
    """
    Convert a value from Eotvos to SI units.

    Parameters:

    * value : number or array
        The value in Eotvos

    Returns:

    * value : number or array
        The value in SI

    """
    return value/fatiando.constants.SI2EOTVOS

def si2mgal(value):
    """
    Convert a value from SI units to mGal.

    Parameters:

    * value : number or array
        The value in SI

    Returns:

    * value : number or array
        The value in mGal

    """
    return value*fatiando.constants.SI2MGAL

def mgal2si(value):
    """
    Convert a value from mGal to SI units.

    Parameters:

    * value : number or array
        The value in mGal

    Returns:

    * value : number or array
        The value in SI

    """
    return value/fatiando.constants.SI2MGAL

def dircos(inc, dec):
    """
    Returns the 3 coordinates of a unit vector given its inclination and
    declination.

    .. note:: Coordinate system is assumed to be x->North, y->East, z->Down.
        Inclination is positive down and declination is measured with respect
        to x (North).

    Parameter:

    * inc : float
        The inclination of the vector (in degrees)
    * dec : float
        The declination of the vector (in degrees)

    Returns:

    * vect : list = [x, y, z]
        The unit vector

    """
    d2r = numpy.pi/180.
    vect = [numpy.cos(d2r*inc)*numpy.cos(d2r*dec),
            numpy.cos(d2r*inc)*numpy.sin(d2r*dec),
            numpy.sin(d2r*inc)]
    return vect

def vecmean(arrays):
    """
    Take the mean array out of a list of arrays.

    Parameter:

    * arrays : list
        List of arrays

    Returns:

    * mean : array
        The mean of each element in the arrays

    Example::

        >>> print vecmean([[1, 1, 2], [2, 3, 5]])
        [ 1.5  2.   3.5]

    """
    return numpy.mean(arrays, axis=0)

def vecstd(arrays):
    """
    Take the standard deviation array out of a list of arrays.

    Parameter:

    * arrays : list
        List of arrays

    Returns:

    * std : array
        Standard deviation of each element in the arrays

    Example::

        >>> print vecstd([[1, 1, 2], [2, 3, 5]])
        [ 0.5  1.   1.5]

    """
    return numpy.std(arrays, axis=0)

class SparseList(object):
    """
    Store only non-zero elements on an immutable list.

    Can iterate over and access elements just like if it were a list.

    Parameters:

    * size : int
        Size of the list.
    * elements : dict
        Dictionary used to initialize the list. Keys are the index of the
        elements and values are their respective values.

    Example::

        >>> l = SparseList(5)
        >>> l[3] = 42.0
        >>> print len(l)
        5
        >>> print l[1], l[3]
        0.0 42.0
        >>> l[1] += 3.0
        >>> for i in l:
        ...     print i,
        0.0 3.0 0.0 42.0 0.0
        >>> l2 = SparseList(4, elements={1:3.2, 3:2.8})
        >>> for i in l2:
        ...     print i,
        0.0 3.2 0.0 2.8

    """

    def __init__(self, size, elements=None):
        self.size = size
        self.i = 0
        if elements is None:
            self.elements = {}
        else:
            self.elements = elements

    def __str__(self):
        return str(self.elements)

    def __len__(self):
        return self.size

    def __iter__(self):
        self.i = 0
        return self

    def __getitem__(self, index):
        if index < 0:
            index = self.size + index
        if index >= self.size or index < 0:
            raise IndexError('index out of range')
        if index not in self.elements:
            return 0.0
        return self.elements[index]

    def __setitem__(self, key, value):
        if key >= self.size:
            raise IndexError('index out of range')
        self.elements[key] = value

    def next(self):
        if self.i == self.size:
            raise StopIteration()
        res = self.__getitem__(self.i)
        self.i += 1
        return res

def sec2hms(seconds):
    """
    Convert seconds into a string with hours, minutes and seconds.

    Parameters:

    * seconds : float
        Time in seconds

    Returns:

    * time : str
        String in the format ``'%dh %dm %2.5fs'``

    Example::

        >>> print sec2hms(62.2)
        0h 1m 2.20000s
        >>> print sec2hms(3862.12345678)
        1h 4m 22.12346s

    """
    h = int(seconds/3600)
    m = int((seconds - h*3600)/60)
    s = seconds - h*3600 - m*60
    return '%dh %dm %2.5fs' % (h, m, s)

def sec2year(seconds):
    """
    Convert seconds into decimal Julian years.

    Julian years have 365.25 days.

    Parameters:

    * seconds : float
        Time in seconds

    Returns:

    * years : float
        Time in years

    Example::

        >>> print sec2year(31557600)
        1.0

    """
    return float(seconds)/31557600.0

def year2sec(years):
    """
    Convert decimal Julian years into seconds.

    Julian years have 365.25 days.

    Parameters:

    * years : float
        Time in years

    Returns:

    * seconds : float
        Time in seconds

    Example::

        >>> print year2sec(1)
        31557600.0

    """
    return 31557600.0*float(years)

def contaminate(data, stddev, percent=False, return_stddev=False):
    """
    Add pseudorandom gaussian noise to an array.

    Noise added is normally distributed.

    Parameters:

    * data : list or array
        Data to contaminate
    * stddev : float
        Standard deviation of the Gaussian noise that will be added to *data*
    * percent : True or False
        If ``True``, will consider *stddev* as a decimal percentage and the
        standard deviation of the Gaussian noise will be this percentage of
        the maximum absolute value of *data*
    * return_stddev : True or False
        If ``True``, will return also the standard deviation used to contaminate
        *data*

    Returns:

    if *return_stddev* is ``False``:

    * contam : array
        The contaminated data array

    else:

    * results : list = [contam, stddev]
        The contaminated data array and the standard deviation used to
        contaminate it.

    """
    log.info("Contaminating data with Gaussian noise:")
    if percent:
        log.info("  noise level = %g percent" % (100*stddev))
        stddev = stddev*max(abs(data))
    log.info("  noise stddev = %s" % (str(stddev)))
    if stddev == 0.:
        if return_stddev:
            return [data, stddev]
        else:
            return data
    contam = numpy.array([numpy.random.normal(v, stddev) for v in data])
    if return_stddev:
        return [contam, stddev]
    else:
        return contam

def normal(x, mean, std):
    """
    Normal distribution.

    .. math::

        N(x,\\bar{x},\sigma) = \\frac{1}{\sigma\sqrt{2 \pi}}
        \exp\\left(-\\frac{(x-\\bar{x})^2}{\sigma^2}\\right)

    Parameters:

    * x : float or array
        Value at which to calculate the normal distribution
    * mean : float
        The mean of the distribution :math:`\\bar{x}`
    * std : float
        The standard deviation of the distribution :math:`\sigma`

    Returns:

    * normal : array
        Normal distribution evaluated at *x*

    """
    return numpy.exp(-1*((mean - x)/std)**2)/(std*numpy.sqrt(2*numpy.pi))

def gaussian(x, mean, std):
    """
    Non-normalized Gaussian function

    .. math::

        G(x,\\bar{x},\sigma) = \exp\\left(-\\frac{(x-\\bar{x})^2}{\sigma^2}
        \\right)

    Parameters:

    * x : float or array
        Values at which to calculate the Gaussian function
    * mean : float
        The mean of the distribution :math:`\\bar{x}`
    * std : float
        The standard deviation of the distribution :math:`\sigma`

    Returns:

    * gauss : array
        Gaussian function evaluated at *x*

    """
    return numpy.exp(-1*((mean - x)/std)**2)

def gaussian2d(x, y, sigma_x, sigma_y, x0=0, y0=0, angle=0.0):
    """
    Non-normalized 2D Gaussian function

    Parameters:

    * x, y : float or arrays
        Coordinates at which to calculate the Gaussian function
    * sigma_x, sigma_y : float
        Standard deviation in the x and y directions
    * x0, y0 : float
        Coordinates of the center of the distribution
    * angle : float
        Rotation angle of the gaussian measure from the x axis (north) growing
        positive to the east (positive y axis)

    Returns:

    * gauss : array
        Gaussian function evaluated at *x*, *y*

    """
    theta = -1*angle*numpy.pi/180.
    tmpx = 1./sigma_x**2
    tmpy = 1./sigma_y**2
    sintheta = numpy.sin(theta)
    costheta = numpy.cos(theta)
    a = tmpx*costheta + tmpy*sintheta**2
    b = (tmpy - tmpx)*costheta*sintheta
    c = tmpx*sintheta**2 + tmpy*costheta**2
    xhat = x - x0
    yhat = y - y0
    return numpy.exp(-(a*xhat**2 + 2.*b*xhat*yhat + c*yhat**2))

def random_points(area, n):
    """
    Generate a set of n random points.

    Parameters:

    * area : list = [x1, x2, y1, y2]
        Area inside of which the points are contained
    * n : int
        Number of points

    Result:

    * points : list
        List of (x, y) coordinates of the points

    """
    x1, x2, y1, y2 = area
    xs = numpy.random.uniform(x1, x2, n)
    ys = numpy.random.uniform(y1, y2, n)
    return numpy.array([xs, ys]).T

def circular_points(area, n, random=False):
    """
    Generate a set of n points positioned in a circular array.

    The diameter of the circle is equal to the smallest dimension of the area

    Parameters:

    * area : list = [x1, x2, y1, y2]
        Area inside of which the points are contained
    * n : int
        Number of points
    * random : True or False
        If True, positions of the points on the circle will be chosen at random

    Result:

    * points : list
        List of (x, y) coordinates of the points

    """
    x1, x2, y1, y2 = area
    radius = 0.5*min(x2 - x1, y2 - y1)
    if random:
        angles = numpy.random.uniform(0, 2*math.pi, n)
    else:
        da = 2.*math.pi/float(n)
        angles = numpy.arange(0., 2.*math.pi, da)
    xs = 0.5*(x1 + x2) + radius*numpy.cos(angles)
    ys = 0.5*(y1 + y2) + radius*numpy.sin(angles)
    return numpy.array([xs, ys]).T

def connect_points(pts1, pts2):
    """
    Connects each point in the first list with all points in the second.
    If the first list has N points and the second has M, the result are 2 lists
    with N*M points each, representing the connections.

    Parameters:

    * pts1 : list
        List of (x, y) coordinates of the points.
    * pts2 : list
        List of (x, y) coordinates of the points.

    Returns:

    * results : lists of lists = [connect1, connect2]
        2 lists with the connected points

    """
    connect1 = []
    append1 = connect1.append
    connect2 = []
    append2 = connect2.append
    for p1 in pts1:
        for p2 in pts2:
            append1(p1)
            append2(p2)
    return [connect1, connect2]
