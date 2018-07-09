import pytest

from astropy.nddata.ccddata import CCDData
from astropy import units as u
from numpy import array, zeros, ones, float64, int64


@pytest.fixture(params=[
    zeros((2,2), dtype=float64), #
    ones((2,2), dtype=float64),
    zeros((2,2), dtype=int64),
    ones((2,2), dtype=int64)
])
def genImages(request):
    return CCDData(request.param, unit=u.electron)

@pytest.fixture(params=[zeros((2,2),dtype=bool), ones((2,2), dtype=bool)])
def genBadPixel(request):
    return CCDData(request.param, unit=u.electron)

from ..ir_reduce import standard_process
def test_standard_process(genImages, genBadPixel):
    standard_process([genImages],genBadPixel,[genImages])
