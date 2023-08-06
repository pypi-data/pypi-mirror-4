import numpy as np
import scipy.signal

def padded_sum(*args):
    """
    Add the :class:`numpy.ndarry` arguments which may be of 
    differing dimensions and sizes, return a :class:`numpy.ndarray`.
    This code is largely based on this Bi Rico's answer to this 
    `Stack Exchange question <http://stackoverflow.com/questions/16180681>`_.
    """
    n = max(a.ndim for a in args)
    args = [a.reshape((n - a.ndim)*(1,) + a.shape) for a in args]
    shp = np.max([a.shape for a in args], 0)
    res = np.zeros(shp)
    for a in args:
        idx = tuple(slice(i) for i in a.shape)
        res[idx] += a
    return res

def convn(A, B) :
    """
    Convolve :class:`numpy.ndarry` arguments *A* and *B*, and
    return the :class:`numpy.ndarry` that results.    
    """
    if any(x.dtype == float for x in [A, B])  :
        return scipy.signal.fftconvolve(A, B)
    else :
        return scipy.signal.convolve(A, B)

def horner(A, *args) :
    """
    Evaluate polynomial with coefficients *A* at all
    of the points given by the equal-sized arrays 
    *args* = *X*, *Y*, ..., (as many as the dimension 
    of *A*). Returns a :class:`numpy.ndarray` of the same size.
    """
    # not yet implemented, this is quite a tricky bit
    # of code
    return 0



