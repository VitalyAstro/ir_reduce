import numpy as np
import astropy
from astropy import units as u
from astropy.nddata import CCDData
import ccdproc
from astropy.stats import SigmaClip
from astropy.io import fits

from typing import List, Tuple, Iterable, Set, Union, Any
from numpy import s_

image_paths = [
    'NCAc070865.fits',
    'NCAc070866.fits',
    'NCAc070867.fits',
    'NCAc070868.fits',
    'NCAc070869.fits',
    'NCAc070870.fits',
    'NCAc070871.fits',
    'NCAc070872.fits',
    'NCAc070873.fits',
    'NCAc070874.fits',
    'NCAc070875.fits',
    'NCAc070876.fits',
    'NCAc070877.fits',
    'NCAc070878.fits',
    'NCAc070879.fits',
    'NCAc070880.fits',
    'NCAc070881.fits',
    'NCAc070882.fits',
    'NCAc070883.fits',
    'NCAc070884.fits',
    'NCAc070885.fits',
    'NCAc070886.fits',
    'NCAc070887.fits',
    'NCAc070888.fits',
    'NCAc070889.fits',
    'NCAc070890.fits',
    'NCAc070891.fits'
]
flat_paths = ['FlatK.fits', 'FlatJ.fits', 'FlatH.fits']
bad_paths = ['bad_zero_sci.fits']

images = [astropy.nddata.CCDData.read(image) for image in image_paths]
flats = [astropy.nddata.CCDData.read(image) for image in flat_paths]
bad = astropy.nddata.CCDData.read(bad_paths[0])

filter_vals = ('H', 'J', 'Ks')
filter_column = 'NCFLTNM2'


def standard_process():
    processed = dict()
    for idx, filter_val in enumerate(filter_vals):
        images_with_filter = [image for image in images if image.header[filter_column] == filter_val]
        flat = flats[idx]

        reduceds = []
        for image in images_with_filter:
            image.mask = bad.data
            # TODO that's from the quicklook-package, probably would want to do this individually for every sensor area
            gain = (image.header['GAIN1'] + image.header['GAIN2'] + image.header['GAIN3'] + image.header['GAIN4']) / 4
            readnoise = (image.header['RDNOISE1'] + image.header['RDNOISE2'] + image.header['RDNOISE3'] + image.header[
                'RDNOISE4']) / 4
            reduced = ccdproc.ccd_process(image,
                                          oscan=None,
                                          error=True,
                                          gain=gain * u.electron / u.count,
                                          # TODO check if this is right or counts->adu required
                                          readnoise=readnoise * u.electron,
                                          dark_frame=None,
                                          master_flat=flat,
                                          bad_pixel_mask=bad.data)
            reduceds.append(reduced)
        processed[filter_val] = reduceds
    return processed


def skyscale(image_list: Iterable[CCDData], method: str = 'subtract',
             cut: Tuple[Union[slice, int]] = s_[200:800, 200:800]) -> List[CCDData]:
    """
    Subtract/divide out the median sky value of some images
    :param image_list: The images to process
    :param method: either 'subtract' or 'divide'
    :param cut: what region of the images to consider to create the median sky value
    :return: images, with sky removed
    """
    sigma_clip = SigmaClip(sigma=3., iters=3)
    filtered_data = [sigma_clip(image.data) for image in image_list]

    medians = np.array([np.median(data[cut]) for data in filtered_data])
    airmass = sum((image.header['AIRMASS'] for image in image_list))  # TODO needed?

    # TODO from original code:
    # Calculate scaling relatively to last image median
    # Why not average or median-median?
    if method == 'subtract':
        medians = medians - medians[-1]
        ret = [CCDData.subtract(image, median*u.electron) for image, median in zip(image_list, medians)]
    elif method == 'divide':
        medians = medians / medians[-1]
        ret = [CCDData.subtract(image, median) for image, median in zip(image_list, medians)]
    else:
        raise ValueError('method needs to be either subtract or divide')

    # TODO: write/return sky file?
    return ret


def interpolate(img: CCDData):
    # TODO combiner does not care about this and marks it invalid still
    from astropy.convolution import Gaussian2DKernel
    from astropy.convolution import interpolate_replace_nans
    kernel = Gaussian2DKernel(1)  # TODO this should be a 9x9 bilinear interpolation

    img.data[img.mask] = np.NaN
    img.data = interpolate_replace_nans(img.data, kernel)

    return img


if __name__ == '__main__':
    processed = standard_process()
    skyscaled = skyscale(processed['J'], 'subtract')
    wcs = skyscaled[0].wcs
    reprojected = [ccdproc.wcs_project(img, wcs) for img in skyscaled]
    output = ccdproc.Combiner(reprojected).median_combine()
    try:
        output.write('pythonTestOut.fits')
    except OSError as err:
        print(err, "...ignoring")
