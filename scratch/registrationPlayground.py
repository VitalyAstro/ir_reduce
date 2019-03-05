from pylab import *
import astropy
from astropy.convolution import convolve_fft as convolve  # this supports wrapping borders around

import image_registration


# https://github.com/keflavich/image_registration/blob/master/image_registration/fft_tools/correlate2d.py
# correlation in terms of convolution

import ir_reduce

processed = ir_reduce.standard_process()
data = processed

i8 = data[8].copy()
i0 = data[0].copy()

# this does not work (aka offset ~0) , due to bad/hot pixels
image_registration.cross_correlation_shifts(i8.data, i0.data, verbose=True)
# image_registration.fft_tools.correlate2d is what it does under the hood


# mean values where mask is set. Maybe interpolate would be better but that didn't help last time as well
i8m = i8.data.copy()
i8m[i8.mask] = i8m.mean()
i0m = i0.data.copy()
i0m[i0.mask] = i8m.mean()

corr = image_registration.fft_tools.correlate2d(i8m, i0m)

astropy.io.fits.writeto("correlationtest.fits",corr,overwrite=True)




