import ir_reduce
import glob
import ccdproc
from astropy.nddata import CCDData
import image_registration

read = ir_reduce.read_and_sort(glob.glob('../testdata/bad*.fits'),
                        glob.glob('../testdata/Flat*.fits'),
                        glob.glob('../testdata/NCA*.fits'))

processed = ir_reduce.tiled_process(read['J'].bad, read['J'].flat[0], read['J'].images)
skyscaled = ir_reduce.skyscale(processed, 'subtract')

interpolated = [ir_reduce.interpolate(image, dofixpix=True) for image in skyscaled]

wcs = interpolated[0].wcs
reprojected = [ccdproc.wcs_project(img, wcs) for img in interpolated]
combined = ccdproc.Combiner(reprojected).median_combine()
#
# first_hdu = output_image.to_hdu()[0]
# scamp_input = CCDData(first_hdu.data, header=first_hdu.header, unit=first_hdu.header['bunit'])
#
# scamp_input = CCDData(first_hdu.data, header=first_hdu.header, unit=first_hdu.header['bunit'])
#

combined.wcs = wcs
combined.write('foo.fits', overwrite=True)
