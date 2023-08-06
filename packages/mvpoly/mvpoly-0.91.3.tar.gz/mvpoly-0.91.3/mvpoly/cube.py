"""

.. class:: MVPolyCube
   :synopsis: Multivariate polynomial class whose 
   coefficient representation is an ND-array

.. moduleauthor:: J.J. Green <j.j.green@gmx.co.uk>

"""

import mvpoly.base
import mvpoly.util.cube

import numbers
import numpy as np

class MVPolyCube(mvpoly.base.MVPoly) :
    """
    Return an object of class :class:`MVPolyCube` with
    the coefficient array set to the optional *coef*
    argument, a :class:`numpy.ndarray`.
    """
    def __init__(self, coef = [], **kwd):
        super(MVPolyCube, self).__init__(**kwd)
        self._coef = np.array(coef, dtype = self.dtype)

    @classmethod
    def monomials(self, n, **kwd) :
        """
        Return a *n*-tuple of each of the monomials (*x*, *y*, ..) 
        of an *n*-variate system.
        """
        return [self.monomial(i, n, **kwd) for i in range(1,n+1)]

    @classmethod
    def monomial(self, i, n, **kwd) :
        """
        Return the *i*-th monomial of an *n*-variate system,
        (*i* = 1, ..., n).
        """
        shp = tuple((1 if i == j else 0) for j in range(1,n+1))
        m = np.zeros([s+1 for s in shp])
        m.itemset(shp, 1)
        return MVPolyCube(m, **kwd)

    def _dtype_set_callback(self, value) :
        self.coef.dtype = value

    @property
    def coef(self) :
        return self._coef

    @coef.setter
    def coef(self, value) :
        self._coef = value

    def __setitem__(self, key, value) :
        """
        The setter method, delegated to the *coef* attribute.
        """
        self.coef[key] = value

    def __getitem__(self, key) :
        """
        The getter method, delegated to the *coef* attribute.
        """
        return self.coef[key]

    def __add__(self, other) :
        """
        Add an :class:`MVPolyCube` to another, or to a :class:`numpy.ndarray`, or 
        to a number; return an :class:`MVPolyCube`.
        """
        a = self.coef
        if isinstance(other, MVPolyCube) :
            b = other.coef
        elif isinstance(other, list) :
            b = np.array(other)
        elif isinstance(other, numbers.Number) :
            b = np.array([other])
        else :
            raise TypeError, "cannot add MVPolyCube to %s" % type(other)
        return MVPolyCube(mvpoly.util.cube.padded_sum(a, b), 
                          dtype = self.dtype)

    def __radd__(self, other) :
        """
        As add, but with the types in the opposite order -- this is
        routed to add.
        """
        return self.__add__(other)

    def __mul__(self, other) :
        """
        Convolve our coefficient array with that of *other*
        and return an :class:`MVPolyCube` object initialised with
        the result.
        """
        if isinstance(other, MVPolyCube) :
            return MVPolyCube(mvpoly.util.cube.convn(self.coef, other.coef),
                              dtype = self.dtype)
        elif isinstance(other, numbers.Number) :
            return MVPolyCube(self.coef * other, dtype = self.dtype)
        else :
            raise TypeError, \
                "cannot multiply MVPolyCube by %s" % type(other)

    def __rmul__(self, other) :
        """
        Reverse order multiply, as add
        """
        return self.__mul__(other)

    def __neg__(self) :
        """
        Negation of a polynomial, return the polynomial with negated 
        coefficients.
        """
        return MVPolyCube(-(self.coef), dtype = self.dtype)

    def __sub__(self, other) :
        """
        Subtraction implemented with add and negate.
        """
        return self + (-other)

    def __rsub__(self, other) :
        """
        Subtraction with reversed arguments.
        """
        return other + (-self)

    def eval(self, *args) :
        """
        Evaluate the polynomial at the points given by *args*.
        There should be as many arguments as the polynomial 
        has variables.  The argument can be numbers, or arrays
        (all of the same shape).
        """
        return mvpoly.util.cube.horner(self.coef, *args)

    def compose(self, *args) :
        """
        Compose polynomials. The arguments, which should be
        :class:`MVPolyCube` polynomials, are substituted 
        into the corresponding variables of the polynomial.
        """
        pass

    def __call__(self, *args) :
        """
        Evaluate or compose polynomials.
        """
        # FIXME : implement the compose route
        return self.eval(*args)

    def diff(*args) :
        """
        Differentiate polynomial. The integer arguments
        should indicate the number to times to differentiate
        with respect to the corresponding polynomial variable,
        hence ``p.diff(0,1,1)`` would correspond to 
        :math:`\partial^2 p / \partial y \partial z`.
        """

    def int(*args) :
        """
        Indefinite integral of polynomial. The arguments are
        as for :meth:`diff`.
        """
