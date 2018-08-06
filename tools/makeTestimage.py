from astropy.nddata import CCDData
import numpy as np
from pylab import *
data = CCDData.read('../testdata/NCAc070888.fits')

checkerboard = np.array(
    [[1,1,0,0],
    [1,1,0,0],
    [0,0,1,1],
    [0,0,1,1]],
    dtype =np.float64
)

pattern = np.zeros((32, 32))
pattern[0,0] = 1
data.data = np.tile(pattern, (data.shape[0]//pattern.shape[0], data.shape[1]//pattern.shape[1]))

#imshow(data)
#show()

data.write('pattern.fits')

