"""
utilities - Several utilities useful when using pyrwt
=====================================================

.. codeauthor:: Amit Aides <amitibo@tx.technion.ac.il>
"""

from __future__ import division
import numpy as np

def hardThreshold(y, thld):
    """
    Hard thresholds the input signal y with the threshold value
    thld.

    Parameters
    ----------
    y : array-like, shape =  Arbitrary dimension
        Finite length signal (implicitly periodized)
    thld : float
        Value by which to threshold the input signal
        
    Returns
    -------
    x : array-like, shape = Same dimension of y
        Hard thresholded output ``x = (abs(y)>thld)*y``

    Examples
    --------
    
    >>> from rwt.utilities import makeSignal, hardThreshold
    >>> y = makeSignal('WernerSorrows', 8)
    >>> print hardThreshold(y, thld=1)
    [1.5545, 5.3175, 0, 1.6956, -1.2678, 0, 1.7332, 0]

    See Also
    --------
    softThreshold
    """
    
    x = np.zeros_like(y)
    ind = np.abs(y) > thld
    x[ind] = y[ind]
    
    return x


def softThreshold(y, thld):
    """
    Soft thresholds the input signal y with the threshold value
    thld.

    Parameters
    ----------
    y : array-like, shape = Arbitrary dimension
        Finite length signal (implicitly periodized)
    thld : float
        Value by which to threshold the input signal
        
    Returns
    -------
    x : array-like, shape = Same dimension as y
        Soft thresholded output x = ``sign(y)(abs(y)-thld)_+``

    Examples
    --------
    >>> from rwt.utilities import makeSignal, hardThreshold
    >>> y = makeSignal('Doppler', 8)
    >>> print softThreshold(y, thld=0.2)
    [0, 0, 0, -0.0703, 0, 0.2001, 0.0483, 0]

    See Also
    --------
    hardThreshold
    """
    
    x = np.abs(y) - thld
    x[x<0] = 0
    x[y<0] = -x[y<0]

    return x


def makeSignal(signal_name='AllSig', N=512):
    """
    Creates artificial test signal identical to the
    standard test signals proposed and used by D. Donoho and I. Johnstone
    in WaveLab (- a matlab toolbox developed by Donoho et al. the statistics
    department at Stanford University).

    Parameters
    ----------
    signal_name : string, optional (default='AllSig')
        Name of the desired signal. Supported values:
            * 'AllSig' (Returns a list with all the signals)
            * 'HeaviSine'
            * 'Bumps'
            * 'Blocks'
            * 'Doppler'
            * 'Ramp'
            * 'Cusp'
            * 'Sing'
            * 'HiSine'
            * 'LoSine'
            * 'LinChirp'
            * 'TwoChirp'
            * 'QuadChirp'
            * 'MishMash'
            * 'Werner Sorrows' (Heisenberg)
            * 'Leopold' (Kronecker)
            
    N : integer, optional (default=512)
        Length in samples of the desired signal

    Returns
    -------
    x : array/list of arrays, shape = [N]

    References
    ----------
    WaveLab can be accessed at
    www_url: http://playfair.stanford.edu/~wavelab/
    Also see various articles by D.L. Donoho et al. at
    web_url: http://playfair.stanford.edu/
    """

    t = np.linspace(1, N, N)/N
    signals = []
    
    if signal_name in ('HeaviSine', 'AllSig'):
        y = 4 * np.sin(4*np.pi*t) - np.sign(t - 0.3) - sign(0.72 - t)
        
        signals.append(y)
    
    if signal_name in ('Bumps', 'AllSig'):
        pos = np.array([ .1, .13, .15, .23, .25, .40, .44, .65, .76, .78, .81])
        hgt = np.array([ 4,  5,   3,   4,  5,  4.2, 2.1, 4.3,  3.1, 5.1, 4.2])
        wth = np.array([.005, .005, .006, .01, .01, .03, .01, .01,  .005, .008, .005])
        y = np.zeros_like(t)
        for p, h, w in zip(pos, hgt, wth):
            y += h/(1 + np.abs((t - p)/w))**4

        signals.append(y)
    
    if signal_name in ('Blocks', 'AllSig'):
        pos = np.array([ .1, .13, .15, .23, .25, .40, .44, .65, .76, .78, .81])
        hgt = np.array([ 4,  -5,   3,   -4,  5,  -4.2, 2.1, 4.3,  -3.1, 2.1, -4.2])
        y = np.zeros_like(t)
        for p, h in zip(pos, hgt):
            y += (1 + np.abs(t - p))*h/2
            
        signals.append(y)

    if signal_name in ('Doppler', 'AllSig'):
        y = np.sqrt(t * (1-t)) * np.sin((2*np.pi*1.05) / (t+.05))
                
        signals.append(y)

    if signal_name in ('Ramp', 'AllSig'):
        y = t.copy()
        y[t >= .37] -= 1
                
        signals.append(y)
    
    if signal_name in ('Cusp', 'AllSig'):
        y = np.sqrt(np.abs(t - 0.37))
                
        signals.append(y)

    if signal_name in ('Sing', 'AllSig'):
        k = np.floor(N * .37)
        y = 1 / np.abs(t - (k+.5)/N)
                
        signals.append(y)

    if signal_name in ('HiSine', 'AllSig'):
        y = np.sin(N*0.6902*np.pi*t)
                
        signals.append(y)

    if signal_name in ('LoSine', 'AllSig'):
        y = np.sin(N*0.3333*np.pi*t)
                
        signals.append(y)

    if signal_name in ('LinChirp', 'AllSig'):
        y = np.sin(N*0.125*np.pi*t*t)
                
        signals.append(y)

    if signal_name in ('TwoChirp', 'AllSig'):
        y = np.sin(N*np.pi*t*t) + np.sin(N*np.pi/3*t*t)
                
        signals.append(y)

    if signal_name in ('QuadChirp', 'AllSig'):
        y = np.sin(N*np.pi/3*t*t*t)
                
        signals.append(y)

    if signal_name in ('MishMash', 'AllSig'):
        #
        # QuadChirp + LinChirp + HiSine
        #
        y = np.sin(N*np.pi/3*t*t*t) + np.sin(N*0.125*np.pi*t*t) + np.sin(N*0.6902*np.pi*t)
                
        signals.append(y)

    if signal_name in ('WernerSorrows', 'AllSig'):
        y = np.sin(N/2*np.pi*t*t*t)
        y += np.sin(N*0.6902*np.pi*t)
        y += np.sin(N*np.pi*t*t)
        
        pos = np.array([.1, .13, .15, .23, .25, .40, .44, .65, .76, .78, .81])
        hgt = np.array([4, 5, 3, 4, 5, 4.2, 2.1, 4.3, 3.1, 5.1, 4.2])
        wth = np.array([.005, .005, .006, .01, .01, .03, .01, .01, .005, .008, .005])
        
        for p, h, w in zip(pos, hgt, wth):
            y += h/(1 + np.abs((t - p)/w))**4

        signals.append(y)

    if signal_name in ('Leopold', 'AllSig'):
        y = (t == np.floor(.37 * N)/N).astype(np.float)
                
        signals.append(y)

    if len(signals) == 1:
        return signals[0]

    return signals