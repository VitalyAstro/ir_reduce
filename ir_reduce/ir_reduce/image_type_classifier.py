from astropy.nddata import CCDData
from .classifier_common import *
from . import notcam_classifier
from . import alfosc_classifier


def determine_instrument(img: CCDData):
    val = img.header['INSTRUME']
    if val == 'ALFOSC_FASU':
        return Instrument.ALFOSC
    if val == 'NOTCAM':
        return Instrument.NOTCAM
    else:
        return Instrument.UNKNOWN


classifiers = {Instrument.NOTCAM: notcam_classifier,
               Instrument.ALFOSC: alfosc_classifier}


def image_category(img: CCDData) -> Category:
    func = classifiers[determine_instrument(img)].image_category
    return func(img)


def band(img: CCDData) -> Band:
    func = classifiers[determine_instrument(img)].band
    return func(img)
