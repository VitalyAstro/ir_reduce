import pytest
import os
from .datadir import datadir

from ir_reduce.image_discovery import discover_header

@pytest.mark.integration
@pytest.mark.filterwarnings('ignore::astropy.wcs.FITSFixedWarning')
@pytest.mark.parametrize('files', ['TestOptData/', 'discoveryTest'])
def test_header_discovery(datadir, files):

    grouped = discover_header(os.path.join(datadir, files))
    assert len(grouped.bad) == 1


