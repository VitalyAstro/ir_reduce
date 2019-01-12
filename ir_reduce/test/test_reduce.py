import pytest

from astropy.nddata.ccddata import CCDData
from astropy import units as u
import warnings
import glob
from numpy import array, zeros, ones, float64, int64, s_
import numpy as np
import os
from ir_reduce import standard_process, skyscale, interpolate, read_and_sort, do_everything
import tempfile

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
def test_read_and_sort():
    testdir = os.path.abspath("../testdata")
    assert os.path.isdir(testdir), testdir + " does not exist"

    bads = glob.glob(testdir + "/bad*.fits")
    flats = glob.glob(testdir + "/Flat*.fits")
    imgs = glob.glob(testdir + "/NCA*.fits")
    read = read_and_sort(bads, flats, imgs)
    assert read['J'].bad
    assert read['J'].flat
    assert len(read['J'].images) > 0
    assert read['H']
    assert read['Ks']


@pytest.mark.integration
@pytest.mark.filterwarnings('ignore::astropy.wcs.FITSFixedWarning')
def test_do_everything():
    testdir = os.path.abspath("../testdata")
    assert os.path.isdir(testdir), testdir + " does not exist"

    bads = glob.glob(testdir + "/bad*.fits")
    flats = glob.glob(testdir + "/Flat*.fits")
    imgs = glob.glob(testdir + "/NCA*.fits")

    with tempfile.TemporaryDirectory() as tmpdir:
        image, scamp, sextractor = do_everything(bads, flats, imgs, os.path.join(tmpdir, "testout_standard.fits"))

        assert image
        assert scamp
        assert sextractor
