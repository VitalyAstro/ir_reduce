#! /bin/python3
from astropy.nddata import CCDData
from pylab import *

data = CCDData.read('../testdata/NCAc070888.fits')

checkerboard = np.array(
    [[1, 1, 0, 0],
     [1, 1, 0, 0],
     [0, 0, 1, 1],
     [0, 0, 1, 1]],
    dtype=np.float64
)

lin_gradient = np.tile(np.linspace(1000, 2000, data.shape[0]), (data.shape[1], 1)).T

pattern = np.zeros((32, 32))
pattern[15, 15] = 1

data.data = np.tile(pattern, (data.shape[0] // pattern.shape[0], data.shape[1] // pattern.shape[1]))
data.data = data.data * lin_gradient

# imshow(data)
# show()

data.write('pattern.fits')
