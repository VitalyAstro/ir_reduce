from typing import Union
import logging

from astropy.nddata import CCDData
from astropy.io.fits import Header
from .classifier_common import Instrument, Category, Band
from . import notcam_classifier
from . import alfosc_classifier


def determine_instrument(indata: Union[CCDData, Header]):
    header = indata.header if hasattr(indata, 'header') else indata
    val = header['INSTRUME']
    if val == 'ALFOSC_FASU':
        return Instrument.ALFOSC
    if val == 'NOTCAM':
        return Instrument.NOTCAM
    else:
        logging.warning('could not determine instrument')
        return Instrument.UNKNOWN


classifiers = {Instrument.NOTCAM: notcam_classifier,
               Instrument.ALFOSC: alfosc_classifier}


def image_category(indata: Union[CCDData, Header]) -> Category:
    func = classifiers[determine_instrument(indata)].image_category
    return func(indata.header) if hasattr(indata, 'header') else func(indata)


def band(indata: Union[CCDData, Header]) -> Band:
    func = classifiers[determine_instrument(indata)].band
    return func(indata.header) if hasattr(indata, 'header') else func(indata)
