from .classifier_common import Band, Category
from astropy.io.fits import Header
import logging

filter_column = 'NCFLTNM2'
filter_values = ('H', 'J', 'Ks')

image_category_str = 'IMAGECAT'
image_type = 'IMAGETYP'
object_ID = 'OBJECT'


def image_category(header: Header) -> Category:
    try:
        cat = header[image_category_str]
        img_type = header[image_type]
    except KeyError:
        logging.warning('could not determine image category')
        return Category.UNKNOWN

    if cat == 'SCIENCE':
        return Category.IMAGING
    elif img_type == 'BAD_PIXEL':
        return Category.BAD
    elif cat == 'CALIB' and 'FLAT' in img_type:
        return Category.FLAT
    else:
        logging.warning('could not determine image category')
        return Category.UNKNOWN


def band(header: Header) -> Band:
    try:
        return Band[header[filter_column]]
    except KeyError as err:
        print(f"Image assumed to be taken with NOTCAM:"
              f" Band {header[filter_column]} not valid for this instrument")
        raise err
