from __future__ import division
import numpy as np
from rwt import dwt, idwt, dwtaxis, idwtaxis
from rwt.wavelets import waveletCoeffs
from rwt.utilities import softThreshold, hardThreshold
import matplotlib.pyplot as plt
from scipy.misc import lena
import os

IMAGES_BASE = 'images'

def savefig(title):
    plt.savefig(os.path.join(IMAGES_BASE, title))


def tutorial1():
    img = lena()
    
    cl, ch, rl, rh = waveletCoeffs('db1')
    img_wavelet, L = dwt(img, cl, ch, L=1)
    
    plt.figure()
    plt.gray()
    plt.imshow(img_wavelet)
    savefig('lena_dwt.png')
    
    
if __name__ == '__main__':
    tutorial1()    
    plt.show()
