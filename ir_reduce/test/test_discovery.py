# flake8: noqa F811
import os

import pytest
from ir_reduce.image_discovery import discover_header

# noinspection PyUnresolvedReferences
from .datadir import datadir


@pytest.mark.integration
@pytest.mark.filterwarnings('ignore::astropy.wcs.FITSFixedWarning')
@pytest.mark.parametrize('files', ['TestOptData/', 'discoveryTest'])
def test_header_discovery(datadir, files):
    grouped = discover_header(os.path.join(datadir, files))
    assert len(grouped.bad) == 1
