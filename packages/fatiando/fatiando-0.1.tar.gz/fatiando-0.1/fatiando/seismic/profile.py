"""
Forward modeling and inversion of seismic profiling data.

**Vertical seismic profiling**

* :func:`~fatiando.seismic.profile.vertical`
* :func:`~fatiando.seismic.profile.ivertical`

Model and invert vertical seismic profiling data. In this kind of profiling, the
wave source is located at the surface on top of the well. The travel-times of
first arrivals is then measured at different depths along the well. The
ith travel-time :math:`t_i` measured at depth :math:`z_i` is a function of the
wave velocity :math:`v_j` and distance :math:`d_{ij}` that it traveled in each
layer

.. math::

    t_i(z_i) = \\sum\\limits_{j=1}^M \\frac{d_{ij}}{v_j}

The distance :math:`d_{ij}` is smaller or equal to the thickness of the layer
:math:`s_j`. Notice that :math:`d_{ij} = 0` if the jth layer is bellow
:math:`z_i`, :math:`d_{ij} = s_j` if the jth layer is above :math:`z_i`, and
:math:`d_{ij} < s_j` if :math:`z_i` is inside the jth layer.

To generate synthetic seismic profiling data, use
:func:`~fatiando.seismic.profile.vertical` like so::

    >>> import fatiando as ft
    >>> # Make the synthetic 4 layer model
    >>> thicks = [10, 20, 10, 30]
    >>> vels = [2, 4, 10, 5]
    >>> # Make an array with the z_i
    >>> zs = [10, 30, 40, 70]
    >>> # Calculate the travel-times
    >>> for t in ft.seismic.profile.vertical(thicks, vels, zs):
    ...     print '%.1f' % (t),
    5.0 10.0 11.0 17.0


To make :math:`t_i` linear with respect to :math:`v_j`, we can use
*slowness* :math:`w_j` instead of velocity

.. math::

    t_i(z_i) = \\sum\\limits_{j=1}^M d_{ij} w_j

This allows us to easily invert for the slowness of each layer, given their
thickness. Here's an example of using
:func:`~fatiando.seismic.profile.ivertical` to do this on some synthetic
data::

    >>> import numpy
    >>> import fatiando as ft
    >>> # Make the synthetic 4 layer model
    >>> thicks = [10, 20, 10, 30]
    >>> vels = [2, 4, 10, 8]
    >>> # Make an array with the z_i
    >>> zs = numpy.arange(5, sum(thicks), 1)
    >>> # Calculate the travel-times
    >>> tts = ft.seismic.profile.vertical(thicks, vels, zs)
    >>> # Make a linear solver and solve for the slowness
    >>> solver = ft.inversion.linear.overdet(nparams=len(thicks))
    >>> p, residuals = ft.seismic.profile.ivertical(tts, zs, thicks, solver)
    >>> for slow in p:
    ...     print '%.1f' % (1./slow),
    2.0 4.0 10.0 8.0

----

"""

import time

import numpy
import numpy.linalg.linalg

from fatiando.seismic import ttime2d
from fatiando.mesher import Square
from fatiando import inversion, utils
import fatiando.logger


log = fatiando.logger.dummy('fatiando.seismic.profile')

class VerticalSlownessDM(inversion.datamodule.DataModule):
    """
    Data module for a vertical seismic profile first-arrival travel-time data.
    Assumes that only the slowness of the layers are parameters in the
    inversion.

    In this case, the inverse problem in linear. The element :math:`G_{ij}` of
    the Jacobian (sensitivity) matrix is given by

    .. math::

        G_{ij} = d_{ij}

    where :math:`d_{ij}` is the distance that the ith first-arrival traveled
    inside the jth layer.

    Uses :func:`fatiando.seismic.ttime2d.straight` for forward modeling to
    build the Jacobian matrix.

    Parameters:

    * traveltimes : list
        The first-arrival travel-times calculated at the measurement stations
    * zp : list
        The depths of the measurement stations (seismometers)
    * thickness : list
        The thickness of each layer in order of increasing depth

    """

    def __init__(self, traveltimes, zp, thickness):
        inversion.datamodule.DataModule.__init__(self, traveltimes)
        self.zp = zp
        self.thickness = thickness
        log.info("  calculating Jacobian (sensitivity) matrix...")
        self.jac_T = self._get_jacobian()

    def _get_jacobian(self):
        nlayers = len(self.thickness)
        zmax = sum(self.thickness)
        z = [sum(self.thickness[:i]) for i in xrange(nlayers + 1)]
        layers = [Square((0, zmax, z[i], z[i + 1]), props={'vp':1.})
                  for i in xrange(nlayers)]
        srcs = [(0, 0)]*len(self.zp)
        recs = [(0, z) for z in self.zp]
        jac_T = numpy.array([ttime2d.straight([l], 'vp', srcs, recs)
                             for l in layers])
        return jac_T

    def get_predicted(self, p):
        return vertical(self.thickness, 1./numpy.array(p), self.zp)

    def sum_gradient(self, gradient, p=None, residuals=None):
        return gradient - 2.*numpy.dot(self.jac_T, self.data)

    def sum_hessian(self, hessian, p=None):
        return hessian + 2.*numpy.dot(self.jac_T, self.jac_T.T)

def vertical(thickness, velocity, zp):
    """
    Calculates the first-arrival travel-times for given a layered model.
    Simulates a vertical seismic profile.

    The source is assumed to be at z = 0. The z-axis is positive downward.

    Parameters:

    * thickness : list
        The thickness of each layer in order of increasing depth
    * velocity : list
        The velocity of each layer in order of increasing depth
    * zp : list
        The depths of the measurement stations (seismometers)

    Returns:

    * travel_times : array
        The first-arrival travel-times calculated at the measurement stations.

    """
    if len(thickness) != len(velocity):
        raise ValueError, "thickness and velocity must have same length"
    nlayers = len(thickness)
    zmax = sum(thickness)
    z = [sum(thickness[:i]) for i in xrange(nlayers + 1)]
    layers = [Square((0, zmax, z[i], z[i + 1]), props={'vp':velocity[i]})
              for i in xrange(nlayers)]
    srcs = [(0, 0)]*len(zp)
    recs = [(0, z) for z in zp]
    return ttime2d.straight(layers, 'vp', srcs, recs)

def ivertical(traveltimes, zp, thickness, solver=None, damping=0., smooth=0.,
    sharp=0., beta=10.**(-10), iterate=False):
    """
    Invert first-arrival travel-time data for the slowness of each layer.

    Parameters:

    * traveltimes : array
        The first-arrival travel-times calculated at the measurement stations
    * zp : list
        The depths of the measurement stations (seismometers)
    * thickness : list
        The thickness of each layer in order of increasing depth
    * solver : function or None
        A linear or non-linear inverse problem solver generated by a factory
        function from a module of package :mod:`~fatiando.inversion`.
        If None, will use a default solver function.
    * damping : float
        Damping regularizing parameter (i.e., how much damping to apply).
        Must be a positive scalar.
    * smooth : float
        Smoothness regularizing parameter (i.e., how much smoothness to apply).
        Must be a positive scalar.
    * sharp : float
        Sharpness (total variation) regularizing parameter (i.e., how much
        sharpness to apply). Must be a positive scalar.

        .. note:: Total variation regularization doesn't seem to work for this
            problem

    * beta : float
        Total variation parameter. See
        :class:`~fatiando.inversion.regularizer.TotalVariation` for details
    * iterate : True or False
        If True, will yield the current estimate at each iteration yielded by
        *solver*. In Python terms, ``iterate=True`` transforms this function
        into a generator function.

    Returns:

    * results : list = [slowness, residuals]:

        * slowness : array
            The slowness of each layer
        * residuals : array
            The inversion residuals (observed travel-times minus predicted
            travel-times by the slowness estimate)

    """
    if damping < 0:
        raise ValueError, "Damping parameter must be positive"
    if smooth < 0:
        raise ValueError, "Smoothness parameter must be positive"
    if len(traveltimes) != len(zp):
        raise ValueError, "traveltimes and zp must have same length"
    nparams = len(thickness)
    if solver is None:
        if not sharp:
            solver = inversion.linear.overdet(nparams)
        else:
            initial = numpy.min(traveltimes)/numpy.max(zp)*numpy.ones(nparams)
            solver = inversion.gradient.levmarq(initial=initial)
    log.info("Invert a vertical seismic profile for slowness:")
    log.info("  number of layers: %d" % (len(thickness)))
    log.info("  iterate: %s" % (str(iterate)))
    log.info("  damping: %g" % (damping))
    log.info("  smoothness: %g" % (smooth))
    log.info("  sharpness: %g" % (sharp))
    log.info("  beta (total variation parameter): %g" % (beta))
    dms = [VerticalSlownessDM(traveltimes, zp, thickness)]
    regs = []
    if damping != 0.:
        regs.append(inversion.regularizer.Damping(damping, nparams))
    if smooth != 0.:
        regs.append(inversion.regularizer.Smoothness1D(smooth, nparams))
    if sharp != 0.:
        regs.append(inversion.regularizer.TotalVariation1D(sharp, nparams,
                                                           beta))
    if iterate:
        return _iterator(dms, regs, solver)
    else:
        return _solver(dms, regs, solver)

def _solver(dms, regs, solver):
    start = time.time()
    try:
        for i, chset in enumerate(solver(dms, regs)):
            continue
    except numpy.linalg.linalg.LinAlgError:
        raise ValueError, ("Oops, the Hessian is a singular matrix." +
                           " Try applying more regularization")
    stop = time.time()
    log.info("  number of iterations: %d" % (i))
    log.info("  final data misfit: %g" % (chset['misfits'][-1]))
    log.info("  final goal function: %g" % (chset['goals'][-1]))
    log.info("  time: %s" % (utils.sec2hms(stop - start)))
    return chset['estimate'], chset['residuals'][0]

def _iterator(dms, regs, solver):
    start = time.time()
    try:
        for i, chset in enumerate(solver(dms, regs)):
            yield chset['estimate'], chset['residuals'][0]
    except numpy.linalg.linalg.LinAlgError:
        raise ValueError, ("Oops, the Hessian is a singular matrix." +
                           " Try applying more regularization")
    stop = time.time()
    log.info("  number of iterations: %d" % (i))
    log.info("  final data misfit: %g" % (chset['misfits'][-1]))
    log.info("  final goal function: %g" % (chset['goals'][-1]))
    log.info("  time: %s" % (utils.sec2hms(stop - start)))
