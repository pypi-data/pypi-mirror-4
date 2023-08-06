"""
Base Regularizer class with the format expected by all inverse problem solvers,
plus a range of regularizing functions already implemented.

**Tikhonov regularization**

* :class:`~fatiando.inversion.regularizer.Damping`
* :class:`~fatiando.inversion.regularizer.Smoothness1D`
* :class:`~fatiando.inversion.regularizer.Smoothness2D`

**Total Variation**

* :class:`~fatiando.inversion.regularizer.TotalVariation1D`
* :class:`~fatiando.inversion.regularizer.TotalVariation2D`

**Equality constraint**

* :class:`~fatiando.inversion.regularizer.Equality`

----

"""

import numpy
import scipy.sparse

import fatiando.logger


log = fatiando.logger.dummy('fatiando.inversion.regularizer')

class Regularizer(object):
    """
    A generic regularizing function module.

    Use this class as a skeleton for building custom regularizer modules, like
    smoothness, damping, total variation, etc.

    Regularizer classes are how each inverse problem solver knows how to
    calculate things like:

    * Value of the regularizing function
    * Gradient of the regularizing function
    * Hessian of the regularizing function

    Not all solvers use all of the above. For examples, heuristic solvers don't
    require gradient and hessian calculations.

    This class has templates for all of these methods so that all solvers know
    what to expect.

    Constructor parameters common to all methods:

    * mu : float
        The regularizing parameter. A positve scalar that controls the tradeoff
        between data fitting and regularization.

    """

    def __init__(self, mu):
        self.mu = mu

    def value(self, p):
        pass

    def sum_gradient(self, gradient, p=None):
        """
        Sums the gradient vector of this regularizer module to *gradient* and
        returns the result.

        Parameters:

        * gradient : array
            The old gradient vector
        * p : array
            The parameter vector

        .. note:: Solvers for linear problems will use ``p = None`` so that the
            class knows how to calculate gradients more efficiently for these
            cases.

        Returns:

        * new_gradient : array
            The new gradient vector

        """
        raise NotImplementedError("sum_gradient method not implemented")

    def sum_hessian(self, hessian, p=None):
        """
        Sums the Hessian matrix of this regularizer module to *hessian* and
        returns the result.

        Parameters:

        * hessian : array
            2D array with the old Hessian matrix
        * p : array
            The parameter vector

        .. note:: Solvers for linear problems will use ``p = None`` so that the
            class knows how to calculate gradients more efficiently for these
            cases.

        Returns:

        * new_hessian : array
            2D array with the new Hessian matrix

        """
        raise NotImplementedError("sum_hessian method not implemented")

class Equality(Regularizer):
    r"""
    Equality constraints.

    Imposes that some or all of the parameters be as close as possible to
    given reference values.

    This regularizing function has the form

    .. math::

        \theta(\bar{p}) = (\bar{p} - \bar{p}^{\thinspace a})^T
        \bar{\bar{A}}^T\bar{\bar{A}}(\bar{p} - \bar{p}^{\thinspace a})

    Vector :math:`\bar{p}^{\thinspace a}` contains the refence values and
    matrix :math:`\bar{\bar{A}}` is a diagonal matrix. The elements in the
    diagonal of :math:`\bar{\bar{A}}` are either 1 or 0. If there is a
    reference for parameter :math:`i`, then :math:`A_{ii} = 1`, else
    :math:`A_{ii} = 0`. Since this is a bit hard to explain, I'll just give an
    example. Suppose there are 3 parameters
    and I want to impose that the second one be as close as possible to the
    number 26. Then,

    .. math::

        \bar{p} =
            \begin{bmatrix}
            p_1 \\ p_2 \\ p_3
            \end{bmatrix} , \quad
        \bar{p}^{\thinspace a} =
            \begin{bmatrix}
            0 \\ 26 \\ 0
            \end{bmatrix} \quad \mathrm{and} \quad
        \bar{\bar{A}} =
            \begin{bmatrix}
            0 & 0 & 0 \\
            0 & 1 & 0 \\
            0 & 0 & 0
            \end{bmatrix}

    The gradient and Hessian matrix are, respectively:

    .. math::

        \bar{g}(\bar{p}) = 2\bar{\bar{A}}^T\bar{\bar{A}}
        \left(\bar{p} - \bar{p}^{\thinspace a} \right)

    and

    .. math::

        \bar{\bar{H}}(\bar{p}) = 2\bar{\bar{A}}^T\bar{\bar{A}}

    Parameters:

    * mu : float
        The regularizing parameter. A positve scalar that controls the tradeoff
        between data fitting and regularization. I.e., how much equality to
        impose
    * reference : dict
        Dictionay with the reference values for the parameters you with to
        constrain. The keys are the indexes of the parameters in the parameter
        vector. The respective values are the reference value for each
        parameter. For example, to constrain parameter 1 to be as close as
        possible to 3.4 and parameter 57 to be as close as possible to 43.7::

            reference = {1:3.4, 57:43.7}

    """

    def __init__(self, mu, reference):
        Regularizer.__init__(self, mu)
        self.reference = reference

    # In practice A^T A = A and we don't actually need any of them

    def value(self, p):
        pa = self.reference
        # A*(p - pa) is a vector with all zeros except for the params with
        # reference values. These are equal to p_k - pa_k
        # The zeros don't enter the norm computation.
        return self.mu*numpy.linalg.norm([p[k] - pa[k] for k in pa])**2

    def sum_gradient(self, gradient, p=None):
        pa = self.reference
        if p is None:
            for k in pa:
                gradient[k] += -2.*self.mu*pa[k]
        else:
            for k in pa:
                gradient[k] += self.mu*2.*(p[k] - pa[k])
        return gradient

    def sum_hessian(self, hessian, p=None):
        for k in self.reference:
            hessian[k][k] += self.mu*2.
        return hessian

class Damping(Regularizer):
    r"""
    Damping regularization. Also known as Tikhonov order 0, Ridge Regression, or
    Minimum Norm.

    Requires that the estimate have its l2-norm as close as possible to zero.

    This regularizing function has the form

    .. math::

        \theta(\bar{p}) = \bar{p}^T\bar{p}

    The gradient and Hessian matrix are, respectively:

    .. math::

        \bar{g}(\bar{p}) = 2\bar{\bar{I}}\bar{p}

    and

    .. math::

        \bar{\bar{H}}(\bar{p}) = 2\bar{\bar{I}}

    where :math:`\bar{\bar{I}}` is the identity matrix.

    Parameters:

    * mu : float
        The regularizing parameter. A positve scalar that controls the tradeoff
        between data fitting and regularization. I.e., how much damping to apply
    * nparams : int
        Number of parameters in the inversion
    * sparse : True or False
        Wether or not to use sparce matrices from scipy

    Examples:

        >>> import numpy
        >>> p = [1, 2, 2]
        >>> hessian = numpy.array([[1, 0, 0], [2, 0, 0], [4, 0, 0]])
        >>> damp = Damping(0.1, nparams=3)
        >>> print damp.value(p)
        0.9
        >>> print damp.sum_hessian(hessian, p)
        [[ 1.2  0.   0. ]
         [ 2.   0.2  0. ]
         [ 4.   0.   0.2]]

    """

    def __init__(self, mu, nparams, sparse=False):
        Regularizer.__init__(self, mu)
        self.eye = self._get_identity(nparams, sparse)

    def _get_identity(self, nparams, sparse):
        if sparse:
            return scipy.sparse.identity(nparams, dtype='f', format='csr')
        else:
            return numpy.identity(nparams)

    def value(self, p):
        return self.mu*numpy.linalg.norm(p)**2

    def sum_gradient(self, gradient, p=None):
        if p is None:
            return gradient
        return gradient + (self.mu*2.)*p

    def sum_hessian(self, hessian, p=None):
        return hessian + (self.mu*2.)*self.eye

class Smoothness(Regularizer):
    r"""
    Smoothness regularization for n-dimensional problems. Imposes that adjacent
    parameters have values as close as possible to each other. What *adjacent*
    means depends of the dimension of the problem. It can be spacially adjacent,
    or just adjacent in the parameter vector, or both.

    This class provides a template for smoothness classes of a specific
    dimension.

    .. warning:: **DON'T USE THIS CLASS DIRECTLY!** Instead, use the
        Smoothness*D classes.

    This regularizing function has the form

    .. math::

        \theta(\bar{p}) = \bar{p}^T\bar{\bar{R}}^T\bar{\bar{R}}\bar{p}

    The gradient and Hessian matrix are, respectively:

    .. math::

        \bar{g}(\bar{p}) = 2\bar{\bar{R}}^T\bar{\bar{R}}\bar{p}

    and

    .. math::

        \bar{\bar{H}}(\bar{p}) = 2\bar{\bar{R}}^T\bar{\bar{R}}

    where :math:`\bar{\bar{R}}` is a finite difference matrix.

    Parameters:

    * mu : float
        The regularizing parameter. A positve scalar that controls the tradeoff
        between data fitting and regularization. I.e., how much smoothness to
        apply.
    * nparams : int
        Number of parameters in the inversion
    * sparse : True or False
        Wether or not to use sparce matrices from scipy

    """

    def __init__(self, mu, nparams, sparse=False):
        Regularizer.__init__(self, mu)
        fdmat = self._makefd(nparams, sparse)
        if sparse:
            self.rtr = fdmat.T*fdmat
            self.value = self._value_sparse
            self.sum_gradient = self._sum_gradient_sparse
        else:
            self.rtr = numpy.dot(fdmat.T, fdmat)
            self.value = self._value
            self.sum_gradient = self._sum_gradient

    def _makefd(self, nparams, sparse):
        raise NotImplementedError("_makefd of Smoothness not implemented")

    def _value(self, p):
        return self.mu*numpy.dot(p.T, numpy.dot(self.rtr, p))

    def _sum_gradient(self, gradient, p=None):
        if p is None:
            return gradient
        return gradient + (self.mu*2.)*numpy.dot(self.rtr, p)

    def _value_sparse(self, p):
        # self.rtr*p returns a dense array, so I have to use numpy.dot for
        # matrix multiplication
        return self.mu*numpy.dot(p.T, self.rtr*p)

    def _sum_gradient_sparse(self, gradient, p=None):
        if p is None:
            return gradient
        return gradient + (self.mu*2.)*self.rtr*p

    def sum_hessian(self, hessian, p=None):
        return hessian + (self.mu*2.)*self.rtr

class Smoothness1D(Smoothness):
    r"""
    Smoothness regularization for 1D problems. Also known as Tikhonov order 1.
    Imposes that adjacent parameters have values as close as possible to each
    other. By adjacent, I mean next to each other in the parameter vector,
    e.g., p[2] and p[3].

    For example, if there are 7 parameters, matrix :math:`\bar{\bar{R}}` will
    be

    .. math::

        \bar{\bar{R}} =
        \begin{bmatrix}
        1 & -1 & 0 & 0 & 0 & 0 & 0\\
        0 & 1 & -1 & 0 & 0 & 0 & 0\\
        0 & 0 & 1 & -1 & 0 & 0 & 0\\
        0 & 0 & 0 & 1 & -1 & 0 & 0\\
        0 & 0 & 0 & 0 & 1 & -1 & 0\\
        0 & 0 & 0 & 0 & 0 & 1 & -1
        \end{bmatrix}

    Parameters:

    * mu : float
        The regularizing parameter. A positve scalar that controls the tradeoff
        between data fitting and regularization. I.e., how much smoothness to
        apply.
    * nparams : int
        Number of parameters in the inversion
    * sparse : True or False
        Wether or not to use sparce matrices from scipy

    """

    def __init__(self, mu, nparams, sparse=False):
        Smoothness.__init__(self, mu, nparams, sparse)

    def _makefd(self, nparams, sparse):
        if sparse:
            raise ValueError(
                "sparse matrices not implemented for 1D smoothness")
        return fdmatrix1d(nparams)

class Smoothness2D(Smoothness):
    r"""
    Smoothness regularization for 2D problems. Also known as Tikhonov order 1.

    Imposes that **spacially** adjacent parameters have values as close as
    possible to each other. By spacially adjacent, I mean that I assume the
    parameters are originaly placed on a grid and the grid is then flattened to
    make the parameter vector.

    For example, if the parameters are on a 2 x 2 grid (for example, in 2D
    linear gravimetric problems), there are 4 parameters on the parameter vector

    .. math::

        \mathrm{grid} =
        \begin{pmatrix}
        p_1 & p_2 \\
        p_3 & p_4
        \end{pmatrix}, \quad
        \bar{p} =
        \begin{pmatrix}
        p_1 \\ p_2 \\
        p_3 \\ p_4
        \end{pmatrix}

    In the case of our example above, the matrix :math:`\bar{\bar{R}}` will be

    .. math::

        \bar{\bar{R}} =
        \begin{bmatrix}
        1 & -1 & 0 & 0 \\
        0 & 0 & 1 & -1 \\
        1 & 0 & -1 & 0 \\
        0 & 1 & 0 & -1 \\
        \end{bmatrix}

    Parameters:

    * mu : float
        The regularizing parameter. A positve scalar that controls the tradeoff
        between data fitting and regularization. I.e., how much smoothness to
        apply.
    * shape : tuple = (ny, nx)
        Number of parameters in each direction of the grid
    * sparse : True or False
        Wether or not to use sparce matrices from scipy

    """

    def __init__(self, mu, shape, sparse=False):
        Smoothness.__init__(self, mu, shape, sparse)

    def _makefd(self, shape, sparse):
        return fdmatrix2d(shape, sparse)

class TotalVariation(Regularizer):
    r"""
    Total variation regularization for n-dimensional problems. Imposes that
    adjacent parameters have values as close as possible to each other, in a
    **l1-norm** sense. What *adjacent* means depends of the dimension of the
    problem. It can be spacially adjacent, or just adjacent in the parameter
    vector, or both.

    "in a l1-norm sense" means that, instead of smoothness, total variation
    imposes **sharpness** on the solution. This means that most parameters will
    be close to each other in value, but a few will be far apart, allowing
    discontinuities to appear.

    This class provides a template for total variation classes of a specific
    dimension.

    .. warning:: **DON'T USE THIS CLASS DIRECTLY!** Instead, use the
        TotalVariation*D classes.

    This regularizing function has the form (Martins et al., 2011)

    .. math::

        \theta(\bar{p}) = \sum\limits_{k=1}^L |v_k|

    where :math:`v_k` is the kth element of vector :math:`\bar{v}`

    .. math::

        \bar{v} = \bar{\bar{R}}\bar{p}

    Function :math:`\theta(\bar{p})` is not differentiable when :math:`v_k`
    approaches zero. We can substitute it with a more friendly version
    (Martins et al., 2011)

    .. math::

        \theta_{\beta}(\bar{p}) = \sum\limits_{k=1}^L
        \sqrt{v_k^2 + \beta}

    :math:`\beta` should be small and controls how close this function is to
    :math:`\theta(\bar{p})`. The larger the value of :math:`\beta` is, the
    closer :math:`\theta_{\beta}` is to the smoothness regularization.

    The gradient and Hessian matrix are, respectively (Martins et al., 2011):

    .. math::

        \bar{g}(\bar{p}) = \bar{\bar{R}}^T \bar{q}(\bar{p})

    and

    .. math::

        \bar{\bar{H}}(\bar{p}) = \bar{\bar{R}}^T\bar{\bar{Q}}(\bar{p})
        \bar{\bar{R}}

    where :math:`\bar{\bar{R}}` is a finite difference matrix, and
    :math:`\bar{q}` and :math:`\bar{\bar{Q}}` are

    .. math::

        \bar{q}(\bar{p}) =
        \begin{bmatrix}
        \frac{v_1}{\sqrt{v_1^2 + \beta}} \\
        \frac{v_2}{\sqrt{v_2^2 + \beta}} \\
        \vdots \\ \frac{v_L}{\sqrt{v_L^2 + \beta}}
        \end{bmatrix}

    and

    .. math::

        \bar{\bar{Q}}(\bar{p}) =
        \begin{bmatrix}
        \frac{\beta}{(v_1^2 + \beta)^{\frac{3}{2}}} & 0 & \ldots & 0 \\
        0 & \frac{\beta}{(v_2^2 + \beta)^{\frac{3}{2}}} & \ldots & 0 \\
        \vdots & \vdots & \ddots & \vdots \\
        0 & 0 & \ldots & \frac{\beta}{(v_L^2 + \beta)^{\frac{3}{2}}}
        \end{bmatrix}

    Parameters:

    * mu : float
        The regularizing parameter. A positve scalar that controls the tradeoff
        between data fitting and regularization. I.e., how much sharpness to
        apply.
    * nparams : int
        Number of parameters in the inversion
    * sparse : True or False
        Wether or not to use sparce matrices from scipy

    References:

    Martins, C. M., W. A. Lima, V. C. F. Barbosa, and J. B. C. Silva, 2011,
    Total variation regularization for depth-to-basement estimate: Part 1 -
    mathematical details and applications: Geophysics, 76, I1-I12.

    """

    def __init__(self, mu, nparams, beta=10.**(-10), sparse=False):
        Regularizer.__init__(self, mu)
        self.fdmat = self._makefd(nparams, sparse)
        self.beta = float(beta)
        if sparse:
            self.value = self._value_sparse
            self.sum_gradient = self._sum_gradient_sparse
            self.sum_hessian = self._sum_hessian_sparse
        else:
            self.value = self._value
            self.sum_gradient = self._sum_gradient
            self.sum_hessian = self._sum_hessian

    def _makefd(self, nparams, sparse):
        raise NotImplementedError("_makefd of TotalVariation not implemented")

    def _value(self, p):
        return self.mu*numpy.linalg.norm(numpy.dot(self.fdmat, p), 1)

    def _value_sparse(self, p):
        return self.mu*numpy.linalg.norm(self.fdmat*p, 1)

    def _sum_gradient(self, gradient, p=None):
        if p is None:
            msg = ("TotalVariation is non-linear and cannot be used with a" +
                   " linear solver.")
            raise ValueError(msg)
        v = numpy.dot(self.fdmat, p)
        self.sqrt = numpy.sqrt(v**2 + self.beta)
        q = v/self.sqrt
        return gradient + self.mu*numpy.dot(self.fdmat.T, q)

    def _sum_gradient_sparse(self, gradient, p=None):
        if p is None:
            msg = ("TotalVariation is non-linear and cannot be used with a" +
                   " linear solver.")
            raise ValueError(msg)
        v = self.fdmat*p
        self.sqrt = numpy.sqrt(v**2 + self.beta)
        q = v/self.sqrt
        return gradient + self.mu*self.fdmat.T*q

    def _sum_hessian(self, hessian, p=None):
        if p is None:
            msg = ("TotalVariation is non-linear and cannot be used with a" +
                   " linear solver.")
            raise ValueError(msg)
        #Qdiag = self.beta/(self.sqrt**3) + 1.
        Qdiag = self.beta/(self.sqrt**3)
        return hessian + self.mu*numpy.dot(self.fdmat.T*Qdiag, self.fdmat)

    def _sum_hessian_sparse(self, hessian, p=None):
        if p is None:
            msg = ("TotalVariation is non-linear and cannot be used with a" +
                   " linear solver.")
            raise ValueError(msg)
        #Qdiag = self.beta/(self.sqrt**3) + 1.
        Qdiag = self.beta/(self.sqrt**3)
        return hessian + self.mu*self.fdmat.T*Qdiag*self.fdmat

class TotalVariation1D(TotalVariation):
    r"""
    Total variation regularization for 1D problems.

    Imposes that adjacent parameters have values as close as possible to each
    other, in a **l1-norm** sense. By adjacent, I mean next to each other in the
    parameter vector, e.g., p[2] and p[3].

    In other words, total variation imposes sharpness on the solution. See
    :class:`~fatiando.inversion.regularizer.TotalVariation` for more
    explanation on this. See
    :class:`~fatiando.inversion.regularizer.Smoothness1D` for details on
    matrix :math:`\bar{\bar{R}}`.


    Parameters:

    * mu : float
        The regularizing parameter. A positve scalar that controls the tradeoff
        between data fitting and regularization. I.e., how much sharpness to
        apply.
    * nparams : int
        Number of parameters in the inversion
    * sparse : True or False
        Wether or not to use sparce matrices from scipy

    """

    def __init__(self, mu, nparams, beta=10.**(-10), sparse=False):
        TotalVariation.__init__(self, mu, nparams, beta, sparse)

    def _makefd(self, nparams, sparse):
        if sparse:
            raise ValueError(
                "sparse matrices not implemented for 1D smoothness")
        return fdmatrix1d(nparams)

class TotalVariation2D(TotalVariation):
    r"""
    Total variation regularization for 1D problems.

    Imposes that spacially adjacent parameters have values as close as possible
    to each other, in a **l1-norm** sense. By spacially adjacent, I mean that I
    assume the parameters are originaly placed on a grid and the grid is then
    flattened to make the parameter vector.

    In other words, total variation imposes sharpness on the solution. See
    :class:`~fatiando.inversion.regularizer.TotalVariation` for more
    explanation on this. See
    :class:`~fatiando.inversion.regularizer.Smoothness2D`
    for details on matrix :math:`\bar{\bar{R}}`.

    Parameters:

    * mu : float
        The regularizing parameter. A positve scalar that controls the tradeoff
        between data fitting and regularization. I.e., how much smoothness to
        apply.
    * shape : tuple = (ny, nx)
        (ny, nx): number of parameters in each direction of the grid
    * sparse : True or False
        Wether or not to use sparce matrices from scipy

    """

    def __init__(self, mu, shape, beta=10.**(-10), sparse=False):
        TotalVariation.__init__(self, mu, shape, beta, sparse)

    def _makefd(self, shape, sparse):
        return fdmatrix2d(shape, sparse)

def fdmatrix1d(n):
    """
    Make a finite difference matrix for a 1D problem.

    See :class:`~fatiando.inversion.regularizer.Smoothness1D` for more
    explanation on this matrix.

    Parameters:

    * n : int
        Number of elements in the parameter vector

    Returns:

    * fdmat : array
        The finite difference matrix for of a 1D problem with n parameters

    """
    fdmat = numpy.zeros((n - 1, n), dtype='f')
    for i in xrange(n - 1):
        fdmat[i][i] = 1
        fdmat[i][i + 1] = -1
    return fdmat

def fdmatrix2d(shape, sparse=False):
    """
    Make a finite difference matrix for a 2D problem.

    See :class:`~fatiando.inversion.regularizer.Smoothness2D` for more
    explanation on this matrix.

    The diagonal derivatives are not taken into account.

    Parameters:

    * shape : tuple = (ny, nx)
        (ny, nx): number of parameters in each direction of the grid
        representing the interpretative model.
    * sparse : True or False
        If True, will use `scipy.sparse.csr_matrix` instead of normal numpy
        arrays

    Returns:

    * fdmat : aray
        The finite difference matrix for of a 2D problem

    """
    ny, nx = shape
    deriv_num = (nx - 1)*ny + (ny - 1)*nx
    rows, cols, values = [], [], []
    deriv_i = 0
    # Derivatives in the x direction
    param_i = 0
    for i in xrange(ny):
        for j in xrange(nx - 1):
            rows.extend([deriv_i, deriv_i])
            cols.extend([param_i, param_i + 1])
            values.extend([1, -1])
            deriv_i += 1
            param_i += 1
        param_i += 1
    # Derivatives in the y direction
    param_i = 0
    for i in xrange(ny - 1):
        for j in xrange(nx):
            rows.extend([deriv_i, deriv_i])
            cols.extend([param_i, param_i + nx])
            values.extend([1, -1])
            deriv_i += 1
            param_i += 1
    fdshape = (deriv_num, nx*ny)
    if sparse:
        fdmat = scipy.sparse.csr_matrix((values, (rows, cols)), fdshape)
    else:
        fdmat = numpy.zeros(fdshape)
        fdmat[rows, cols] = values
    return fdmat
