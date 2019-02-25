from enum import Enum
from astropy.nddata import CCDData
from . import NotcamClassifier
from . import AlfoscClassifier


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
    UNKNOWN = 2


def determine_instrument(img: CCDData):
    val = img.header['INSTRUME']
    if val == 'ALFOSC_FASU':
        return Instrument.ALFOSC
    if val == 'NOTCAM':
        return Instrument.NOTCAM
    else:
        return Instrument.UNKNOWN


classifiers = {Instrument.NOTCAM: NotcamClassifier,
               Instrument.ALFOSC: AlfoscClassifier}


def image_category(img: CCDData) -> Category:
    func = classifiers[determine_instrument(img)].image_category
    return func(img)


def band(img: CCDData) -> Band:
    func = classifiers[determine_instrument(img)].band
    return func(img)
