## Prerequisites
Python >= 3.6, Astropy, ccdproc

Recommended:
pytest, tox, sphinx, coverage

## Installation
As this tool is still likely buggy installation is recommended with

`pip install -e /path/to/ir_reduce`
or
`python /path/to/ir_reduce/setup.py develop`

## Tools
* **pytest** Finds everything that looks like a test case and runs it

* **coverage** shows you which lines of code are actually exercised by the tests and which branches/functions are not tested

* **tox** Tool for test automation on different python versions. Creates a virtual environment for you, installs the package and runs various tests

* **sphinx** creates documentation, also from comments in code

## Files:
* **setup.py** What pip/easy\_install etc. uses to install the package
* **MANIFEST** Which files will also be included in the package
* **default.conv, sextractor.conf, scamp.conf, default.param** Config files for SExtractor and Scamp

* **tox.ini** config file for tox
* **conftest.py** add option to pytest to run integration/end-to-end tests that depend on testdata and are slow with --runintegration

## Tests
There are two kinds of tests: Unit tests that verify that a given function/unit works well and integration/end-to-end tests that work on real data. For them to work scamp and SExtractor must be installed, available as `scamp` and `sex` in the PATH and a directory "testdata" be present that contains the "NCA*.fits" exposures "Flat[HJK].fits" and "bad_*.fits" bad pixel maps

## Some example usages
run tests: `pytest`

run tests with testdata/network access: `ir_reduce$ pytest --runintegration` (testdata-directory must be present in parent dir)

run tests, linter, doc-build and coverage in isolated environment: `tox`

run documentation build:
`cd docs; make html`


