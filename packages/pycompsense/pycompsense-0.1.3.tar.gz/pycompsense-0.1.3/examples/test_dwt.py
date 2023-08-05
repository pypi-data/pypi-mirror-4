"""

"""

from __future__ import division
import numpy as np
import scipy as sp
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import pywt

def func(node, *args, **kwargs):
    print node.data
    return False
    
def main():
    """
    Main Function
    """

    x = np.array([np.arange(16)] * 16, 'd')
    wp = pywt.WaveletPacket2D(data=x, wavelet='db1', mode='sym', maxlevel=2)
    data = [n.data for n in wp.get_leaf_nodes(decompose=True)]
    d = np.array(data)
    new_wp = pywt.WaveletPacket2D(data=None, wavelet='db1', mode='sym', maxlevel=2)
    data = [n.data for n in new_wp.get_leaf_nodes(decompose=True)]
    print data
    print d.shape
    print data
    
if __name__ == '__main__':
    main()