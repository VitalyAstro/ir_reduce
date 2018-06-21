import astropy
from astropy import wcs
from astropy.io import fits

# extract header from initial file, also
header=fits.open('FlatH.fits')[0].header 
header.totextfile('brokenheader.txt')
header.tofile('brokenheader')

#re-read header, this is not strictly necessary but shows that the issue is indeed just the header
#either of
header=astropy.io.fits.header.Header.fromtextfile('brokenheader.txt')
header=astropy.io.fits.header.Header.fromfile('brokenheader')
 
wcs_object = wcs.WCS(header=header,relax=False) # works
wcs_object.to_header() #Boom

