## Prerequisites
Python >= 3.6, Astropy, ccdproc

Recommended:
pytest, tox, sphinx, coverage

## Installation
As this tool is still likely buggy, installation is recommended with

`pip install -e /path/to/ir_reduce`
or
`python /path/to/ir_reduce/setup.py develop`

This allows you to import the module from anywhere in the system, while still being to edit it in the original directory
## Tools
* **pytest** Finds everything that looks like a test case and runs it

* **coverage** shows you which lines of code are actually exercised by the tests and which branches/functions are not tested

* **tox** Tool for test automation on different python versions. Creates a virtual environment for you, installs the package and runs various tests

* **sphinx** creates documentation, also from comments in code

## Files:
### Source Files
* **run_sextractor_scamp.py** use SExtractor and scamp to extract sources from either fits-files or CCDData objects
and return/write an astrometric solution
* **image_discovery** Find all files in a given directory that look like fits-images
* **ir_reduce.py** The main file. Offers reduction facilities for CCD-images.
`do_everything` is putting it all together. Good starting point to read

### Helpers
* **setup.py** What pip/easy\_install etc. uses to install the package
* **MANIFEST** Which files will also be included in the package
* **default.conv, sextractor.conf, scamp.conf, default.param** Config files for SExtractor and Scamp

* **tox.ini** config file for tox
* **conftest.py** add option to pytest to run integration/end-to-end tests that depend on testdata and are slow with --runintegration

### Misc

* **scratch** contains experiments that use or where used to build the library. Don't expect to be able to run them
but maybe they give some context/ideas

* **tools** contains some scripts to create test images and profile a typical run of the reduction toolchain, profiler
outputs gperf and kcachegrind compatible files


## Tests
There are two kinds of tests: Unit tests that verify that a given function/unit works well and integration/end-to-end tests that work on real data.
For them to work scamp and SExtractor must be installed, available as `scamp` and `sex` in the PATH and a directory "testdata" be present
that contains the "NCA*.fits" exposures "Flat[HJK].fits" and "bad_*.fits" bad pixel maps

## Some example usages
### using the CLI
the cli is installed as a script called "ir-reduce-cli". You can also run ir\_reduce/cli.py. Supports --help

specify bad/flat/exposures manually:
`ir-reduce-cli manual -f Flat* -b bad_* -e MYImages*.fits` -o output.fits

`manual` can be shortened to `m`. Discovery mode is still a little experimental

Discover all files in current directory with filter Band H
`ir-reduce-cli --filter H d`

Discover all files in specified directory with filter Band J(default)
`ir-reduce-cli d /some/other/dir`

Only astroreference H_pnv.fits
 `ir-reduce-cli ref -i H_pnv.fits`


Reduce, astroreff images. Plot reference cataloge and source exctractor results
 `mkdir wdir
  ir-reduce-cli -v --filter J m -i ../NCAc0708*fits -f ../Flat* -b ../bad_*  --wdir wdir
  ir-reduce-cli t reduced.fits wdir/sexout.fits wdir/GAIA-DR1_1726+4220_r4.cat`

### Usage from python
run tests: `pytest`

run tests with testdata/network access: `ir_reduce$ pytest --runintegration` (testdata-directory must be present in parent dir)

run tests, linter, doc-build and coverage in isolated environment: `tox`

run documentation build:
`cd docs; make html`

use the module (see also run\_defaults in parent directory)
```import ir_reduce

#
   image, scamp, sextractor =
        ir_reduce.do_everything(['./testdata/bad_zero_sci.fits'], ['./testdata/FlatJ.fits'], glob.glob('./testdata/NCAc0708*.fits'),
                    output='pythonout.fits')

# astroref a single file with scamp
ir_reduce.astroref_file('./testdata/reduced/H_16eg.fits','./testdata/reduced/H_16eg_astroreffed')

# returns a dict of CCDData by filter
read = ir_reduce.read_and_sort(glob.glob('../testdata/bad*.fits'),
                        glob.glob('../testdata/Flat*.fits'),
                        glob.glob('../testdata/NCA*.fits'))

#only do the ccdproc-internal steps for files from the J filter
processed = ir_reduce.tiled_process(read['J'].bad, read['J'].flat[0], read['J'].images)

# skyscale an image using subtraction
skyscaled = ir_reduce.skyscale(processed, 'subtract')

```



