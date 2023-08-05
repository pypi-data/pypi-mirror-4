"""
rwt - Implementaion of wavelet transforms
=========================================

.. codeauthor:: Amit Aides <amitibo@tx.technion.ac.il>
"""

from __future__ import division
import numpy as np
cimport numpy as np
from rwt cimport *

DTYPEd = np.double
ctypedef np.double_t DTYPEd_t


def _prepareInputs(src_array, h, L):

    src_array = np.array(src_array, dtype=DTYPEd, copy=False, order='C')
    if src_array.ndim > 1:
        m, n = src_array.shape
    else:
        m = 1
        n = src_array.size

    h = np.array(h, dtype=DTYPEd, copy=False, order='C')
    if h.ndim > 1:
        h_row, h_col = h.shape
    else:
        h_row = 1
        h_col = h.size
    
    if h_col > h_row:
        lh = h_col
    else:    
        lh = h_row
        
    if L == None:
        #
        # Estimate L
        #
        i = n
        j = 0
        while i % 2 == 0:
            i >>= 1
            j += 1

        L = m
        i = 0
        while L % 2 == 0:
            L >>= 1
            i += 1
	    
        if min(m, n) == 1:
            L = max(i, j)
        else:
            L = min(i, j)
        
    assert(L != 0, "Maximum number of levels is zero; no decomposition can be performed!")
    assert(L > 0, "The number of levels, L, must be a non-negative integer")

    #
    # Check the ROW dimension of input
    #
    if m > 1:
        mtest = m / 2.0**L
        assert(mtest == int(mtest), "The matrix row dimension must be an integer multiplication of 2**L")

    #
    # Check the COLUMN dimension of input
    #
    if n > 1:
        ntest = n / 2.0**L
        assert(ntest == int(ntest), "The matrix column dimension must be an integer multiplication of 2**L")
        
    return src_array, L, m, n, lh


def dwt(x, h, L=None):
    """	
    Computes the discrete wavelet transform y for a 1D or 2D input
    signal x using the scaling filter h.

    Parameters
    ----------
    x : array-like, shape = [n] or [m, n]
        Finite length 1D or 2D signal (implicitly periodized)
    h : array-like, shape = [n]
        Scaling filter
    L : integer, optional (default=None)
        Number of levels. In the case of a 1D signal, length(x) must be
        divisible by 2**L; in the case of a 2D signal, the row and the
        column dimension must be divisible by 2**L. If no argument is
        specified, a full DWT is returned for maximal possible L.

    Returns
    -------
    y : array-like, shape = [n] or [m, n]
        The wavelet transform of the signal 
        (see example to understand the coefficients)
    L : integer
	number of decomposition levels

    Examples
    --------
    2D Example:

    >>> from scipy.misc import lena
    >>> from rwt import dwt, idwt
    >>> from rwt.utilities import makeSignal
    >>> from rwt.wavelets import daubcqf
    >>> img = lena()
    >>> h = daubcqf(4, 'min')[0]
    >>> L = 1
    >>> y, L = dwt(img, h, L)

    See Also
    --------
    idwt, rdwt, irdwt

    """
    
    x, L, m, n, lh = _prepareInputs(x, h, L)

    cdef np.ndarray[DTYPEd_t, ndim=1]  np_x = np.array(x, dtype=DTYPEd, copy=False, order='C').ravel()
    cdef np.ndarray[DTYPEd_t, ndim=1]  np_h = np.array(h, dtype=DTYPEd, copy=False, order='C').ravel()
    cdef np.ndarray[DTYPEd_t, ndim=1]  np_y = np.zeros(x.size, dtype=DTYPEd)
    
    MDWT(
        <double *>np_x.data,
        m,
        n,
        <double *>np_h.data,
        lh,
        L,
        <double *>np_y.data
        );
    
    y = np_y.copy()
    y.shape = x.shape
    
    return y, L


def idwt(y, h, L=None):
    """
    Computes the inverse discrete wavelet transform x for a 1D or
    2D input signal y using the scaling filter h.

    Parameters
    ----------
    y : array-like, shape = [n] or [m, n]
        Finite length 1D or 2D input signal (implicitly periodized)
	(see function mdwt to find the structure of y)
    h : array-like, shape = [n]
        Scaling filter
    L : integer, optional (default=None)
        Number of levels. In the case of a 1D signal, len(x) must be
        divisible by 2**L; in the case of a 2D signal, the row and the
        column dimension must be divisible by 2**L. If no argument is
        specified, a full DWT is returned for maximal possible L.

    Returns
    -------
    x : array-like, shape = [n] or [m, n]
        Periodic reconstructed signal
    L : integer
	Number of decomposition levels

    Examples
    --------
    1D Example:
    
    >>> from rwt import dwt, idwt
    >>> from rwt.utilities import makeSignal
    >>> from rwt.wavelets import daubcqf
    >>> xin = makeSignal('LinChirp', 8)
    >>> h = daubcqf(4, 'min')[0]
    >>> L = 1
    >>> y, L = dwt(xin, h, L)
    >>> print y
    [0.1912, 0.8821, 1.4257, 0.3101, -0.0339, 0.1001, 0.2201, 0.0000]
    >>> x, L = idwt(y, h, L)
    >>> print x
    [0.0491, 0.1951, 0.4276, 0.7071, 0.9415, 0.9808, 0.6716, 0.0000]

    See Also
    --------
    dwt, rdwt, irdwt
    """
    
    y, L, m, n, lh = _prepareInputs(y, h, L)
    
    cdef np.ndarray[DTYPEd_t, ndim=1]  np_x = np.zeros(y.size, dtype=DTYPEd)
    cdef np.ndarray[DTYPEd_t, ndim=1]  np_h = np.array(h, dtype=DTYPEd, copy=False, order='C').ravel()
    cdef np.ndarray[DTYPEd_t, ndim=1]  np_y = np.array(y, dtype=DTYPEd, copy=False, order='C').ravel()
    
    MIDWT(
        <double *>np_x.data,
        m,
        n,
        <double *>np_h.data,
        lh,
        L,
        <double *>np_y.data
        );
    
    x = np_x.copy()
    x.shape = y.shape
    
    return x, L


def rdwt(x, h, L=None):
    """
    Computes the redundant discrete wavelet transform y
    for a 1D  or 2D input signal. (Redundant means here that the
    sub-sampling after each stage is omitted.) yl contains the
    lowpass and yh the highpass components. In the case of a 2D
    signal, the ordering in yh is 
    [lh hl hh lh hl ... ] (first letter refers to row, second to
    column filtering). 

    Parameters
    ----------
    x : array-like, shape = [n] or [m, n]
        Finite length 1D or 2D signal (implicitly periodized)
    h : array-like, shape = [n]
        Scaling filter
    L : integer, optional (default=None)
        Number of levels. In the case of a 1D signal, len(x) must be
        divisible by 2**L; in the case of a 2D signal, the row and the
        column dimension must be divisible by 2**L. If no argument is
        specified, a full DWT is returned for maximal possible L.

    Returns
    -------
    yl : array-like, shape = [n] or [m, n]
        Lowpass component
    yh : array-like, shape = [n] or [m, n]
        Highpass component
    L : integer
	number of decomposition levels
	
    See Also
    --------
    dwt, idwt, irdwt

    Warnings
    --------
    min(x.shape)/2**L should be greater than len(h)

    """

    x, L, m, n, lh = _prepareInputs(x, h, L)
    
    cdef np.ndarray[DTYPEd_t, ndim=1]  np_x = np.array(x, dtype=DTYPEd, copy=False, order='C').ravel()
    cdef np.ndarray[DTYPEd_t, ndim=1]  np_h = np.array(h, dtype=DTYPEd, copy=False, order='C').ravel()
    cdef np.ndarray[DTYPEd_t, ndim=1]  np_yl = np.zeros(x.size, dtype=DTYPEd)
    cdef np.ndarray[DTYPEd_t, ndim=2]  np_yh
    
    if min(m, n) == 1:
        np_yh = np.zeros((m, L*n), dtype=DTYPEd)
    else:
        np_yh = np.zeros((m, 3*L*n), dtype=DTYPEd)

    MRDWT(
        <double *>np_x.data,
        m,
        n,
        <double *>np_h.data,
        lh,
        L,
        <double *>np_yl.data,
        <double *>np_yh.data
        );
    
    yl = np_yl.copy()
    yl.shape = x.shape
    
    return yl, np_yh, L
    

def irdwt(yl, yh, h, L=None):
    """
    Computes the inverse redundant discrete wavelet
    transform x  for a 1D or 2D input signal. (Redundant means here
    that the sub-sampling after each stage of the forward transform
    has been omitted.) yl contains the lowpass and yl the highpass
    components as computed, e.g., by mrdwt. In the case of a 2D
    signal, the ordering in
    yh is [lh hl hh lh hl ... ] (first letter refers to row, second
    to column filtering).  

    Parameters
    ----------
    yl : array-like, shape = [n] or [m, n]
        Lowpass component
    yh : array-like, shape = [n] or [m, n]
        Highpass component
    h : array-like, shape = [n]
        Scaling filter
    L : integer
	number of levels. In the case of a 1D signal, 
	len(yl) must  be divisible by 2**L;
	in the case of a 2D signal, the row and
	the column dimension must be divisible by 2**L.	
   
    Returns
    -------
    x : array-like, shape = [n] or [m, n]
        Finite length 1D or 2D signal
    L : integer
	number of decomposition levels

    See Also
    --------
    dwt, idwt, rdwt

    Warnings
    --------
    min(yl.shape)/2**L should be greater than len(h)

    """

    yl, L, m, n, lh = _prepareInputs(yl, h, L)
    
    yh = np.array(yh, copy=False, order='C')
    mh, nh = yh.shape
    
    #
    # check for consistency of rows and columns of yl, yh
    #
    if min(m, n) > 1:
        assert(m == mh and nh == 3*n*L, "Dimensions of first two input matrices not consistent!")
    else:
        assert(m == mh and nh == n*L, "Dimensions of first two input vectors not consistent!")

    cdef np.ndarray[DTYPEd_t, ndim=1]  np_x = np.zeros(yl.size, dtype=DTYPEd)
    cdef np.ndarray[DTYPEd_t, ndim=1]  np_h = np.array(h, dtype=DTYPEd, copy=False, order='C').ravel()
    cdef np.ndarray[DTYPEd_t, ndim=1]  np_yl = np.array(yl, dtype=DTYPEd, copy=False, order='C').ravel()
    cdef np.ndarray[DTYPEd_t, ndim=1]  np_yh = np.array(yh, dtype=DTYPEd, copy=False, order='C').ravel()
    
    MIRDWT(
        <double *>np_x.data,
        m,
        n,
        <double *>np_h.data,
        lh,
        L,
        <double *>np_yl.data,
        <double *>np_yh.data
        );
    
    x = np_x.copy()
    x.shape = yl.shape
    
    return x, L
    
    
def _prepareInputs2(src_array, h, L, axis):

    src_array = np.array(src_array, dtype=DTYPEd, copy=False, order='C')
    
    assert(axis >= 0 and axis <= src_array.ndim, "Wrong axis value")
    
    shape = src_array.shape
    prod_h = int(np.prod(shape[:axis]))
    stride = int(np.prod(shape[axis+1:]))
    n = shape[axis]
    
    h = np.array(h, dtype=DTYPEd, copy=False, order='C').ravel()
    lh = h.size
        
    if L == None:
        #
        # Estimate L
        #
        i = n
        L = 0
        while i % 2 == 0:
            i >>= 1
            L += 1

    assert(L != 0, "Maximum number of levels is zero; no decomposition can be performed!")
    assert(L > 0, "The number of levels, L, must be a non-negative integer")

    return src_array, L, n, stride, prod_h, lh


def dwtaxis(x, h, axis=0, L=None):
    """	
    Computes the discrete wavelet transform over signal x
    along a specific axis using the scaling filter h.

    Parameters
    ----------
    x : array-like, shape = Arbitrary dimension
        Input signal
    h : array-like, shape = [n]
        Scaling filter
    axis : integer, optional (default=0)
        The axis of x for which to perform the transform.
    L : integer, optional (default=None)
        Number of levels. In the case of a 1D signal, length(x) must be
        divisible by 2**L; in the case of a 2D signal, the row and the
        column dimension must be divisible by 2**L. If no argument is
        specified, a full DWT is returned for maximal possible L.

    Returns
    -------
    y : array-like, shape = Same dimension of x.
        The wavelet transform of the input signal 
    L : integer
	number of decomposition levels

    See Also
    --------
    idwt, rdwt, irdwt, idwtaxis

    """
    
    
    x, L, n, stride, prod_h, lh = _prepareInputs2(x, h, L, axis)
    
    y = np.empty(x.shape, dtype=DTYPEd, order='C')
    
    cdef np.ndarray[DTYPEd_t, ndim=1]  np_x = np.array(x, dtype=DTYPEd, copy=False, order='C').ravel()
    cdef np.ndarray[DTYPEd_t, ndim=1]  np_h = np.array(h, dtype=DTYPEd, copy=False, order='C').ravel()
    cdef np.ndarray[DTYPEd_t, ndim=1]  np_y = y.ravel()
    
    DWTAXIS(
        <double *>np_x.data,
        n,
	prod_h,
	stride,
        <double *>np_h.data,
        lh,
        L,
        <double *>np_y.data
        );
    
    return y, L


def idwtaxis(y, h, axis=0, L=None):
    """	
    Computes the inverse discrete wavelet transform over signal x
    along a specific axis using the scaling filter h.

    Parameters
    ----------
    y : array-like, shape = Arbitrary dimension
        Input signal
    h : array-like, shape = [n]
        Scaling filter
    axis : integer, optional (default=0)
        The axis of x for which to perform the transform.
    L : integer, optional (default=None)
        Number of levels. In the case of a 1D signal, length(x) must be
        divisible by 2**L; in the case of a 2D signal, the row and the
        column dimension must be divisible by 2**L. If no argument is
        specified, a full DWT is returned for maximal possible L.

    Returns
    -------
    x : array-like, shape = Same dimension of x.
        The inverse wavelet transform of the input signal 
    L : integer
	number of decomposition levels

    See Also
    --------
    idwt, rdwt, irdwt, dwtaxis

    """
    
    
    y, L, n, stride, prod_h, lh = _prepareInputs2(y, h, L, axis)
    
    x = np.empty(y.shape, dtype=DTYPEd, order='C')
    
    cdef np.ndarray[DTYPEd_t, ndim=1]  np_y = np.array(y, dtype=DTYPEd, copy=False, order='C').ravel()
    cdef np.ndarray[DTYPEd_t, ndim=1]  np_h = np.array(h, dtype=DTYPEd, copy=False, order='C').ravel()
    cdef np.ndarray[DTYPEd_t, ndim=1]  np_x = x.ravel()
    
    IDWTAXIS(
        <double *>np_x.data,
        n,
	prod_h,
	stride,
        <double *>np_h.data,
        lh,
        L,
        <double *>np_y.data
        );
    
    return x, L


