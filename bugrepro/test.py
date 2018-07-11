import faulthandler
faulthandler.enable()
from astropy.io import fits
header = fits.Header()
header['SIMPLE'] = 'T'
header['BITPIX'] = -32
header['NAXIS'] = 2
header['NAXIS1'] = 256
header['NAXIS2'] = 256
header['OBSGEO-X'] = 12.2124214124
from astropy.wcs import WCS
wcs = WCS(header)
wcs.to_header()


