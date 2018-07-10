"""
Module for reducing infrared Data, currently for NOTCam but intended for a future instrument
"""
import numpy as np
import astropy
import os
import itertools
from astropy import units as u
from astropy.nddata import CCDData
import ccdproc
from astropy.stats import SigmaClip
from astropy.io import fits
from .image_discovery import Paths

from functools import reduce  # TODO meh, maybe rename this file then...

from typing import List, Tuple, Iterable, Set, Union, Any, Dict
from numpy import s_  # numpy helper to create slices by indexing this

# Globals: Fits-columns #todo: put in module
filter_column = 'NCFLTNM2'  # TODO NOTCam-specific
filter_vals = ('H', 'J', 'Ks')

image_category = 'IMAGECAT'
object_ID = 'OBJECT'


def read_and_sort(bads: Iterable[str], flats: Iterable[str], exposures: Iterable[str]) -> Dict[str, Paths]:
    """

    :param bads:
    :param flats:
    :param exposures:
    :return:
    """
    # TODO move asserts into unit-test or introduce a validation flag/wrapper
    assert (all(os.path.isfile(path) for path in itertools.chain(bads, flats, exposures)))

    image_datas = [astropy.nddata.CCDData.read(image) for image in exposures]
    flat_datas = [astropy.nddata.CCDData.read(image) for image in flats]
    bad_datas = [astropy.nddata.CCDData.read(image) for image in bads]

    ret = dict()
    # for all filter present in science data we need at least a flatImage and a bad pixel image
    for filter_id in filter_vals:
        try:
            images_with_filter = [image for image in image_datas if image.header[filter_column] == filter_id]
            # only science images allowed
            assert (all((image.header[image_category] == 'SCIENCE' for image in images_with_filter)))

            flats_with_filter = [image for image in flat_datas if image.header[filter_column] == filter_id]
            #assert (len(flats_with_filter) == 1)  # TODO only one flat
            # TODO this assumes that you pass all possible flats. But CLI only wants one flat right now
        except KeyError as err:
            print("looks like there's no filter column in the fits data")
            raise err

        # bad pixel maps are valid, no matter the filter
        ret[filter_id] = Paths(bad_datas, flats_with_filter, images_with_filter)

    return ret


# TODO standard_process(bads,flats,images) -> List[CCDData]
def standard_process(bads: List[CCDData], flat: CCDData, images: List[CCDData]) -> List[CCDData]:
    bad = reduce(lambda x, y: x.astype(bool) | y.astype(bool), (i.data for i in bads))  # combine bad pixel masks

    reduceds = []
    for image in images:
        image.mask = bad
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
                                      bad_pixel_mask=bad)
        reduceds.append(reduced)
    return reduceds


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
        medians = (medians - medians[-1])
        ret = [CCDData.subtract(image, median * u.electron) for image, median in zip(image_list, medians)]
    elif method == 'divide':
        medians = medians / medians[-1]
        ret = [CCDData.subtract(image, median * u.electron) for image, median in zip(image_list, medians)]
    else:
        raise ValueError('method needs to be either subtract or divide')

    # TODO: write/return sky file?
    return ret


def fixPix(im, mask):
    import scipy.ndimage as ndimage
    """
    taken from https://www.iaa.csic.es/~jmiguel/PANIC/PAPI/html/_modules/reduce/calBPM.html#fixPix 
    (GPLv3)
    
    Applies a bad-pixel mask to the input image (im), creating an image with
    masked values replaced with a bi-linear interpolation from nearby pixels.
    Probably only good for isolated badpixels.

    Usage:
      fixed = fixpix(im, mask, [iraf=])

    Inputs:
      im = the image array
      mask = an array that is True (or >0) where im contains bad pixels
      iraf = True use IRAF.fixpix; False use numpy and a loop over
             all pixels (extremelly low)

    Outputs:
      fixed = the corrected image

    v1.0.0 Michael S. Kelley, UCF, Jan 2008

    v1.1.0 Added the option to use IRAF's fixpix.  MSK, UMD, 25 Apr
           2011

    Notes
    -----
    - Non-IRAF algorithm is extremelly slow.
    """

    # create domains around masked pixels
    dilated = ndimage.binary_dilation(mask)
    domains, n = ndimage.label(dilated)

    # loop through each domain, replace bad pixels with the average
    # from nearest neigboors
    y, x = np.indices(im.shape, dtype=np.int)[-2:]
    # x = xarray(im.shape)
    # y = yarray(im.shape)
    cleaned = im.copy()
    for d in (np.arange(n) + 1):
        # find the current domain
        i = (domains == d)

        # extract the sub-image
        x0, x1 = x[i].min(), x[i].max() + 1
        y0, y1 = y[i].min(), y[i].max() + 1
        subim = im[y0: y1, x0: x1]
        submask = mask[y0: y1, x0: x1]
        subgood = (submask == False)

        cleaned[i * mask] = subim[subgood].mean()

    return cleaned

def interpolate(img: CCDData, dofixpix=False):
    # TODO combiner does not care about this and marks it invalid still
    from astropy.convolution import CustomKernel
    from astropy.convolution import interpolate_replace_nans

    if dofixpix:
        print("begin fixpix")
        img.data = fixPix(img.data,img.mask)
        print("end fixpix")
    else:
        # TODO this here doesn't really work all that well -> extended regions cause artifacts at border
        kernel_array=astropy.array([[1,1,1],[1,1,1],[1,1,1]])/9 # average of all surrounding pixels
        kernel = CustomKernel(kernel_array)  # TODO the original pipeline used fixpix, which says it uses linear interpolation

        img.data[np.logical_not(img.mask)] = np.NaN
        img.data = interpolate_replace_nans(img.data, kernel)

    return img


def do_everything(bads: Iterable[str],
                  flats: Iterable[str],
                  images: Iterable[str],
                  output: str,
                  filter: str = 'J', #TODO: allow 'all'
                  combine: str ='median',
                  skyscale_method: str = 'subtract',
                  register: bool = False,
                  verbosity: int = 0,
                  force: bool = False):

    assert(filter in filter_vals)
    read_files = read_and_sort(bads, flats, images)[filter]
    # TODO distortion correct
    processed = standard_process(read_files.bad, read_files.flat[0], read_files.images)
    skyscaled = skyscale(processed, skyscale_method)

    interpolated = [interpolate(image, dofixpix=True) for image in skyscaled]

    wcs = interpolated[0].wcs
    reprojected = [ccdproc.wcs_project(img, wcs) for img in interpolated]
    # TODO align to this if register True
    output_image = ccdproc.Combiner(reprojected).median_combine()
    output_image.wcs = wcs
    #TODO MOST important: registration
    try:
        output_image.write(output, overwrite='True')
    except OSError as err:
        print(err, "writing output failed")
    return output_image




# todo move everything below to testcase
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
bad_paths = ['bad_cold5.fits', 'bad_zero_sci.fits', 'bad_hot2.fits']

if __name__ == '__main__':
    images = [astropy.nddata.CCDData.read(image) for image in image_paths]
    flats = [astropy.nddata.CCDData.read(image) for image in flat_paths]
    bads = [astropy.nddata.CCDData.read(image) for image in bad_paths]
    bad = reduce(lambda x, y: x.astype(bool) | y.astype(bool), (i.data for i in bads))  # combine bad pixel masks

    read_files = read_and_sort(bad_paths, flat_paths, image_paths)

    processed = standard_process(read_files['J'].bad, read_files['J'].flat[0], read_files['J'].images)
    skyscaled = skyscale(processed, 'subtract')
    wcs = skyscaled[0].wcs
    reprojected = [ccdproc.wcs_project(img, wcs) for img in skyscaled]
    output = ccdproc.Combiner(reprojected).median_combine()
    try:
        output.write('pythonTestOut.fits')
    except OSError as err:
        print(err, "...ignoring")
