# flake8: noqa F811
import glob
import os
import tempfile

import numpy as np
import pytest
from astropy import units as u
from astropy.nddata.ccddata import CCDData
from ir_reduce import standard_process, skyscale, interpolate, read_and_sort, do_everything, Pool, PoolDummy
from ir_reduce.classifier_common import Band
from numpy import zeros, ones, float64, int64, s_

# noinspection PyUnresolvedReferences
from .datadir import datadir # noqa

# Setup
image_size = (10, 10)


@pytest.fixture(params=[
    zeros(image_size, dtype=float64),
    ones(image_size, dtype=float64),
    zeros(image_size, dtype=int64),
    ones(image_size, dtype=int64)
])
def genImages(request):
    ret = CCDData(request.param, unit=u.count)
    for i in range(1, 5):
        ret.header["GAIN" + str(i)] = 1
        ret.header["RDNOISE" + str(i)] = 1
        ret.header["AIRMASS"] = 1
    return ret


@pytest.fixture(params=[zeros(image_size, dtype=bool), ones(image_size, dtype=bool)])
def genBadPixel(request):
    return CCDData(request.param, unit=u.electron)


# testcases
@pytest.mark.filterwarnings('ignore:invalid value encountered in true_divide:RuntimeWarning')
def test_standard_process_smoke(genImages, genBadPixel):
    """Smoke-test: Does anything explode?"""
    standard_process([genImages], genBadPixel, [genImages])


def test_skyscale_smoke(genImages):
    genImages.unit = u.electron
    skyscale([genImages], cut=s_[1, 9])
    skyscale([genImages, genImages], cut=s_[1, 9])


def test_interpolate():
    """TODO Test if the kernel convolution is actually a bilinear interpolation"""
    ccd = CCDData(ones((11, 11), dtype=float64), unit=u.dimensionless_unscaled)

    # everything valid, but set middle pixel to a bogus value and invalid
    ccd.mask = ccd.data.astype(bool)
    ccd.mask[5, 5] = False
    ccd.data[5, 5] = -12423.23

    ccdCorr = interpolate(ccd.copy())
    assert ccdCorr.data[5, 5] == 1.0

    # all pixels around the invalid pixel are 10 -> pixel should become 10 as well
    ccd.data[4:7, 4:7] = 10
    ccdCorr = interpolate(ccd.copy())
    assert np.isclose(ccdCorr.data[5, 5], 10)


# test for copying behaviour of function chain

@pytest.mark.integration
@pytest.mark.filterwarnings('ignore::astropy.wcs.FITSFixedWarning')
@pytest.mark.parametrize('pool', [PoolDummy(), Pool(2)])
def test_read_and_sort(pool, datadir):
    assert os.path.isdir(datadir), datadir + " does not exist"

    bads = glob.glob(datadir + "/bad*.fits")
    flats = glob.glob(datadir + "/Flat*.fits")
    imgs = glob.glob(datadir + "/NCA*.fits")
    read = read_and_sort(bads, flats, imgs, pool)
    assert read[Band.J].bad
    assert read[Band.J].flat
    assert len(read[Band.J].images) > 0
    assert read[Band.J]
    assert read[Band.J]


@pytest.mark.integration
@pytest.mark.filterwarnings('ignore::astropy.wcs.FITSFixedWarning')
def test_do_everything_ir(datadir):
    assert os.path.isdir(datadir), datadir + " does not exist"

    bads = glob.glob(datadir + "/bad*.fits")
    flats = glob.glob(datadir + "/Flat*.fits")
    imgs = glob.glob(datadir + "/NCA*.fits")

    with tempfile.TemporaryDirectory() as tmpdir:
        image, scamp, sextractor = do_everything(bads, flats, imgs, os.path.join(tmpdir, "testout_standard.fits"))

        assert image
        assert scamp
        assert sextractor


@pytest.mark.integration
@pytest.mark.filterwarnings('ignore::astropy.wcs.FITSFixedWarning')
def test_do_everything_optical(datadir):
    assert os.path.isdir(datadir), datadir + " does not exist"

    imgs = [os.path.join(datadir, "TestOptData", img) for img in
            ["ALAd210081.fits", "ALAd210082.fits", "ALAd210080.fits", "ALAd210079.fits"]]
    bads = []
    flats = [os.path.join(datadir, "TestOptData", flat) for flat in
             ['ALAd210014.fits',
              'ALAd210016.fits',
              'ALAd210032.fits',
              'ALAd210038.fits',
              'ALAd210027.fits',
              'ALAd210026.fits',
              'ALAd210028.fits',
              'ALAd210040.fits',
              'ALAd210034.fits',
              'ALAd210022.fits',
              'ALAd210024.fits',
              'ALAd210012.fits',
              'ALAd210011.fits',
              'ALAd210007.fits',
              'ALAd210039.fits',
              'ALAd210035.fits',
              'ALAd210010.fits',
              'ALAd210019.fits',
              'ALAd210008.fits',
              'ALAd210031.fits',
              'ALAd210030.fits',
              'ALAd210023.fits',
              'ALAd210002.fits',
              'ALAd210006.fits',
              'ALAd210015.fits',
              'ALAd210036.fits',
              'ALAd210020.fits',
              'ALAd210018.fits',
              'ALAd210003.fits',
              'ALAd210004.fits']]

    with tempfile.TemporaryDirectory() as tmpdir:
        image, scamp, sextractor = do_everything(bads, flats, imgs, os.path.join(tmpdir, "testout_standard.fits"),
                                                 band_id=Band.vbes)

        assert image
        assert scamp
        assert sextractor
