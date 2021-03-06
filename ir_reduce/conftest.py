import pytest


def pytest_addoption(parser):
    parser.addoption(
        "--runintegration", action="store_true", default=False, help="run integration tests depending on testdata"
    )
    parser.addoption(
        "--data-dir", action='store', default='../testdata', help="custom directory for testdata"
    )
    parser.addoption(
        "--dummy", action="store_true", default=False, help="dummy argument"
    )


def pytest_collection_modifyitems(config, items):
    if config.getoption("--runintegration"):
        # --runintegration given in cli: do not skip slow tests
        return
    skip_int = pytest.mark.skip(reason="need --runintegration option to run")
    for item in items:
        if "integration" in item.keywords:
            item.add_marker(skip_int)
