from .classifier_common import Band, Category
from astropy.nddata import CCDData

filter_column = 'NCFLTNM2'
filter_values = ('H', 'J', 'Ks')

image_category_str = 'IMAGECAT'
object_ID = 'OBJECT'


def image_category(img: CCDData) -> Category:
    val = img.header[image_category_str]
    if val == 'SCIENCE':
        return Category.SCIENCE
    elif val == 'CALIB':
        return Category.CALIBRATION
    else:
        return Category.UNKNOWN


def band(img: CCDData) -> Band:
    try:
        return Band[img.header[filter_column]]
    except KeyError as err:
        print(f"Image assumed to be taken with NOTCAM:"
              f" Band {img.header[filter_column]} not valid for this instrument")
        raise err
