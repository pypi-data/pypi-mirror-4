from rtools.colormap import *



def test_colormap():

    rmap = RColorMap("dummy")
    try:
        m = rmap.colormap()
    except:
        pass

    rmap = RColorMap("heat")
    m = rmap.colormap()
    try:
        import numpy as np
        import pylab as plt
        A = np.array(range(100))
        A.shape = (10,10)
        plt.pcolor(A,cmap=m, vmin=0, vmax=100)
        plt.colorbar()
        #plt.savefig('example.png')
    except:
        pass
