import pytest
from astropy.nddata import CCDData
import os
import glob

from ir_reduce import image_type_classifier
from .datadir import datadir

@pytest.mark.integration
@pytest.mark.filterwarnings('ignore::astropy.wcs.FITSFixedWarning')
@pytest.mark.parametrize('files', ['TestOptData/*.fits', '*.fits'])
def test_classification_smoke(datadir,files):
    datas = [CCDData.read(fname) for fname in glob.glob(os.path.join(datadir, 'TestOptData/*.fits'))]

    for data in datas:
        image_type_classifier.determine_instrument(data)
        image_type_classifier.image_category(data)
        image_type_classifier.band(data)
