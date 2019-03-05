import pytest


@pytest.fixture
def datadir(request):
    """Enables passing custom data directory as command line parameter"""
    return request.config.option.data_dir
