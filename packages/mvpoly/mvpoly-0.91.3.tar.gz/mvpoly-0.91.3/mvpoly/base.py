class MVPoly(object) :
    """
    Base (new-style) class for MVPoly 
    """

    def __init__(self, dtype = float) :
        self._dtype = dtype 

    # subclasses are encouraged to overide the method
    # _dtype_set_callback(value) below, it can set the
    # the datatype of the representation.

    def _dtype_set_callback(value) :
        pass

    @property
    def dtype(self) :
        return self._dtype

    @dtype.setter
    def dtype(self, value) :
        self._dtype_set_callback(value)
        self._dtype = value

    def intd(p, *intervals) :
        """
        Evaluate the definite integral polynomial *p*
        over the cube determined by the *intervals*.
        """

    def maxmodnd(p, epsilon = 1e-12, verbose = False, i0 = None) :
        """
        The maximum modulus of a complex *n*-variate polynomial *p* on 
        the unit *n*-polydisc is estimated using a method of repeated 
        subdivision of :math:`[0,2\pi]^n` and rejection of non-maximizing 
        *n*-cubes. 

        The rejection criterion is based on a lemma of S.B. Steckin,
        extended to *n*-variate polynomials by G. De La Chevrotiere [#DLC]_.

        :param p: the multivatiate polynomial
        :type p: an MVPoly subclass instance
        :param epsilon: relative precision required
        :type epsilon: float
        :param verbose: set run-time information 
        :type verbose: bool
        :param i0: initial number of intervals
        :type i0: a vector of integers
        :rtype: a tuple (*M*, *t*, *h*, *evals*) 

        Here  *M* is the estimate of the maximum modulus of *p*;
        *t* is an *n*-column matrix whose rows are the midpoints of 
        non-rejected *n*-cubes; *h* is the half-width 
        of non-rejected *n*-cubes; *evals* is the total number of 
        evaluations of the polynomial used.

        .. [#DLC]
            G. De La Chevrotiere. *Finding the maximum modulus of a
            polynomial on the polydisk using a generalization of 
            Steckin's lemma*, SIAM Undergrad. Res. Online, 2, 2009.    
        
        """
        # FIXME - put the e-graves back in Chevrotiere, encoding bollocks
        pass

    def _binary_pow(self, n) :
        """
        Integer power implemented by binary division.
        """
        p = self
        if n == 1 :
            return p
        if n % 2 == 0 :
            p = p._binary_pow(n/2)
            return p * p
        else :
            return p * p._binary_pow(n-1);

    def __pow__(self, n) :
        """
        Integer power using a repeated-multiplication method, subclasses may 
        choose to implement a more efficient method (FFT and so on) for their 
        particular data-representation.
        """
        if not isinstance(n, int) :
            raise TypeError, "bad power exponent type"
        if n < 0 :
            raise ArithmeticError, "cannot handle negative integer powers"
        if n == 0 :
            return self.__init___(1, dtype = self.dtype)

        return self._binary_pow(n)
