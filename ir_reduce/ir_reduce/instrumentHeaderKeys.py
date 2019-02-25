from enum import Enum
from astropy.nddata import CCDData


class Category(Enum):
    SCIENCE = 0
    CALIBRATION = 1
    UNKNOWN = 2


class Band(Enum):
    H = 'H'
    J = 'J'
    Ks = 'Ks'


class Instrument(Enum):
    NOTCAM = 0
    ALFOSC = 1


def determine_instrument(img: CCDData):
    pass


# notcam
filter_column = 'NCFLTNM2'  # TODO NOTCam-specific
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
        print(f"Image assumed to be taken with NOTCAM: Band {img.header[filter_column]} not valid for this instrument")
        raise err


