"""
Everything you need to solve inverse problems!

The main components of this package are:

**Regularizing functions**

* :mod:`~fatiando.inversion.regularizer`

This module has many classes that implement a range of regularizing functions.
These classes know how to calculate the Hessian matrix, gradient vector, and
value of the regularizing function for a given parameter vector. Most of these
classes are generic and can be applied to any inverse problem, though some are
designed for a specific parametrization (2D or 3D grids, for example).

The regularizer classes can be passed to any inverse problem solver (bellow).

See the :class:`~fatiando.inversion.regularizer.Regularizer` class for the
general structure the solvers expect from regularizer classes.

**Inverse problem solvers**

* :mod:`~fatiando.inversion.linear`
* :mod:`~fatiando.inversion.gradient`
* :mod:`~fatiando.inversion.heuristic`

These modules have factory functions that generate generic inverse problem
solvers. Instead of solving the inverse problem, they return a solver function
with they solver parameters (step size, maximum iterations, etc) already set.
The solver functions are actually Python generators_. Generators are special
Python functions that have a ``yield`` statement instead of a ``return``. The
difference is that generators should be used in ``for`` loops and return one
iteration of the solving process per loop iteration.

The solver functions receive only two parameters: a list of data modules
(see :mod:`~fatiando.inversion.datamodule`) and a list of regularizers
(see :mod:`~fatiando.inversion.regularizer`). Data modules know how to calculate
things like the Hessian matrix and gradient vector for a given data set and
parametrization (specific to a given inverse problem). Regularizers know how to
calculate the same things but for a given regularizing function and
parametrization. This way, the user can combine any number of data sets and
regularizers as he/she wants. So we can program the solvers and regularizers
once and use them in any inverse problem!

.. _generators: http://wiki.python.org/moin/Generators

A typical factory function for an iterative solver looks like::

    def factory(initial, step, maxit):
        # Define the solver generator. The parameters need by this specific
        # solver are passed to it as optional parameters.
        # dms is a list of data modules and regs is a list of regularizers
        def solver(dms, regs, initial=initial, step=step, maxit=maxit):
            # Initialize the solver parameters
            ...
            for it in xrange(maxit):
                # Do an iteration and find an estimate p
                ...
                # Now comes the cool part! Spit out a changeset with the result
                # of this iteration in a dictionary. goals is a list of the
                # goal function values until this iteration. misfits is the same
                # but for the data-misfit function. residuals is a list of the
                # residual vectors of each data module
                yield {'estimate':p, 'goals':goals, 'misfits':misfits,
                       'residuals':residuals}
        # The factory function returns the solver function (Python magic) which
        # can be passed to a particular inverse problem.
        return solver


**Example of using a solver**

Lets say I have a module that solves a particular inverse problem called
``myinvprob.py``. This module would look something like this::

    # myinvprob.py
    from fatiando import inversion

    class MyDataModule(inversion.datamodule.DataModule):
        \"""
        My personal data module. Implements the methods in the DataModule class
        for this specific problem.
        \"""
        def __init__(self, data):
            ...
        ...

    # Make a solver for this inverse problem using damping regularization
    def solve(data, solver, damping=0):
        \"""
        Damping solver.

        Parameters:
        ...
        * solver
            A solver generator produced by a factory function

        \"""
        dms = [MyDataModule(data)]
        regs = [inversion.regularizer.Damping(damping)]
        # Now, run all iterations until the solver generator stops
        for chset in solver(dms, regs):
            continue
        # collect the results from the last changeset
        estimate = chset['estimate']
        # and return
        return estimate

    # You can also make an generator solver for this problem. This way the user
    # can run through the iterations to see how they progress
    def iterate(data, solver, damping=0):
        ...
        # Define data modules and regularizers the same way
        ...
        # But this time, yield the estimate at each iteration
        for chset in solver(dms, regs):
            yield chset['estimate']


These solvers can then be called from scripts, like so::

    # My script
    from fatiando import myinvprob
    from fatiando.inversion import gradient

    # Load the data or generate synthetic data and pick an initial estimate
    ...

    # Solve the problem using Newton's method
    solver = gradient.newton(initial, maxit=100, tol=10**(-5))

    # Solve it all in one go
    estimate = myinvprob.solve(data, solver, damping=0.1)

    # or run through the iterations, plotting each step
    for estimate in myinvprob.iterate(data, solver, damping=0.1):
        # Plot estimate
        ...


**Real usage examples**

Some modules that use the :mod:`~fatiando.inversion` API:

* :mod:`fatiando.seismic.profile`
* :mod:`fatiando.seismic.srtomo`
* :mod:`fatiando.seismic.epic2d`
* :mod:`fatiando.geothermal.climsig`
* :mod:`fatiando.gravmag.basin2d`

----

"""

from fatiando.inversion import (datamodule,
                                regularizer,
                                gradient,
                                heuristic,
                                linear)

