"""
wavelets - A wavelet libray.
============================

A library of functions that create different kinds of wavelets.

.. codeauthor:: Amit Aides <amitibo@tx.technion.ac.il>
"""

from __future__ import division
import numpy as np
import scipy as sp


def daubcqf(N, TYPE='min'):
    """
    Computes the Daubechies' scaling and wavelet filters (normalized to sqrt(2)).

    Parameters
    ----------
    N : int
        Length of filter (must be even)
    TYPE : ['min', 'max', 'mid'], optional (default='min')
        Distinguishes the minimum phase, maximum phase and mid-phase solutions
        ('min', 'max', or 'mid').
        
    Returns
    -------
    h_0 : array-like, shape = [N]
        Daubechies' scaling filter 
    h_1 : array-like, shape = [N]
        Daubechies' wavelet filter 

    Examples
    --------
    >>> from rwt.wavelets import daubcqf
    >>> h_0, h_1 = daubcqf(N=4, TYPE='min')
    >>> print h_0, h_1
    [[0.4830, 0.8365, 0.2241, -0.1294]] [[0.1294, 0.2241, -0.8365, 0.4830]]
    """

    assert N%2==0, 'No Daubechies filter exists for odd length'

    K = int(N/2)
    a = 1
    p = 1
    q = 1
    
    h_0 = np.array([1.0, 1.0])
    for j in range(1, K):
        a = -a * 0.25 * (j + K - 1)/j
        h_0 = np.hstack((0, h_0)) + np.hstack((h_0, 0))
        p = np.hstack((0, -p)) + np.hstack((p, 0))
        p = np.hstack((0, -p)) + np.hstack((p, 0))
        q = np.hstack((0, q, 0)) + a * p

    q = np.sort(np.roots(q))
    
    qt = q[:K-1]
    
    if TYPE == 'mid':
        if K%2==1:
            ind = np.hstack((np.arange(0, N-2, 4), np.arange(1, N-2, 4)))
        else:
            ind = np.hstack(
                (
                    1,
                    np.arange(3, K-1, 4),
                    np.arange(4, K-1, 4),
                    np.arange(N-3, K, -4),
                    np.arange(N-4, K, -4)
                )
            )
        qt = q[ind]

    h_0 = np.convolve(h_0, np.real(np.poly(qt)))
    h_0 = np.sqrt(2) * h_0 / np.sum(h_0)
    
    h_0.shape = (1, -1)
    
    if TYPE=='max':
        h_0 = sp.fliplr(h_0);

    assert np.abs(np.sum(h_0 ** 2))-1 < 1e-4, 'Numerically unstable for this value of "N".'

    h_1 = sp.rot90(h_0, 2).copy()
    h_1[0, :N:2] = -h_1[0, :N:2]

    return (h_0, h_1)


if __name__ == '__main__':
    
    N = 4
    TYPE = 'min'
    h_0, h_1 = daubcqf(N, TYPE)
    print h_0
    print h_1
    