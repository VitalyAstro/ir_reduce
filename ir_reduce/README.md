## What is this?

A tool to take individual exposures from the Nordic Optical Telescope's NOTCAM and ALFSOC instruments and performing
reduction, astroreferencing, coordinate system correction in one go and produce an output suitable for transient detection

## Prerequisites
Python >= 3.6, Astropy, ccdproc

installed astromatic tools: sextractor >= 2.25, scamp >= 2.6.7 (somewhere in PATH at least)

Recommended:
pytest, tox, sphinx, coverage

## Installation
As this tool is still likely buggy, installation is recommended with

`pip install -e /path/to/ir_reduce`
or
`python /path/to/ir_reduce/setup.py develop`

This allows you to import the module from anywhere in the system, while still being to edit it in the original directory
## used Tools
* **pytest** Finds everything that looks like a test case and runs it.

* **coverage** shows you which lines of code are actually exercised by the tests and which branches/functions are not tested

* **tox** Tool for test automation on different python versions. Creates a virtual environment for you, installs the package and runs various tests

* **sphinx** creates documentation, also from comments in code. This is a little overkill for now as it contains
no extra info, better would be to read this readme file and look at the docstrings in the code. 

## Files:
### Source Files
* **run_sextractor_scamp.py** use SExtractor and scamp to extract sources from either fits-files or CCDData objects
and return/write an astrometric solution
* **image_discovery** Find all files in a given directory that look like fits-images
* **ir_reduce.py** The main file. Offers reduction facilities for CCD-images.
`do_everything` is putting it all together. Good starting point to read
* **\*classifier\*.py** logic to determine instrument, spectral band and type (calibration/science...) of image

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
that contains the "NCA*.fits" exposures "Flat\[HJK\].fits" and "bad_*.fits" bad pixel maps.
Additionaly for the optical data, "TestOptData" needs to be present, containing the "ALAd210*.fits" files. 
For testing the image discovery logic, the directory "discoveryTest" should contain a subset of infrared data, with at least one image being a bad-pixel map and containing the fits-image tag IMAGETYP=BAD_PIXEL

The code has been written with type annotations, so you can use the built-in inspector of e.g. pycharm or mypy
to find inconsistent function usage. Right now especially the astropy types cause still a bunch of false positives, 
hence you get the output in a tox-run but it's not counted as an error

To run tests, cd to  <git root>/ir\_reduce and run `pytest`. To run integration tests, invoke `pytest --runintegration`, to point to a custom testdata-directory use `pytest --datadir /path/to/data/dir`

To get an idea which parts of the code are exercised by the tests run `coverage run -m pytest`.
This is automatically done by tox, along with a style-check.
Generally it's a good idea to write at least a "smoke test" (can this be run at all?) 
for a change as the type checking can't really discover most problems, especially those related to the incoming
data format (like header-keywords) and wrong usage of scamp/sextractor. 
 

you can also pass these arguments to tox, like so: `tox -- --runintegration --datadir /path/to/data`

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

Discover files based on fits-header, not filename (potentially slower)
`ir-reduce-cli d --method header /dir/`

Only astroreference H_pnv.fits
 `ir-reduce-cli ref -i H_pnv.fits`


Reduce, astroreff images. Plot reference cataloge and source exctractor results
 `mkdir wdir
  ir-reduce-cli -v --filter J m -i ../NCAc0708*fits -f ../Flat* -b ../bad_*  --wdir wdir
  ir-reduce-cli t reduced.fits wdir/sexout.fits wdir/GAIA-DR1_1726+4220_r4.cat`

Reduce images in current directory for the V_bes filter, sort them by header
    `ir-reduce-cli -fl "V_Bes 530_80" d --method header ./`
  

### Usage from python
run tests: `pytest`

run tests with testdata/network access: `ir_reduce$ pytest --runintegration` (testdata-directory must be present in parent dir)

run tests, linter, doc-build and coverage in isolated environment: `tox`

run documentation build:
`cd docs; make html`

use the module (see also run\_defaults in parent directory)
```
import ir_reduce

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

### Troubleshooting

There will be a lot of warnings, mostly from astropy. For the most parts these can be ignored.
The easiest way to debug assertion errors or other exceptions would be to either run the script
under pdb `pdb ir-reduce-cli {args}`, from an ide like pycharm/spyder with the inbuilt debugger attached
or use the reduction functions interactively from ipython and then running `%debug` after an exception has occured


## State of the Software/Architecture

The general approach behind this tool was to forgoe an object orriented approach in favour of data-in, data-out functions
As the extension to use both NOTCAM and ALFSOC data was done late in the development process and both these Instruments
seem to have certain quirks in the data (Header keywords, image size, combination of filter wheels) this has gotten a little messy
and a bunch of hardcoded, instrument specific logic and todos are scattered through the code. 
This talk gives a good overview of how a clean separation could work https://www.destroyallsoftware.com/talks/boundaries
without busting out the full might and verbosity of object oriented approaches.

Mostly PEP8 style is followed, but for the trial/experiment scripts often don't conform. Also in some places
shadowing of variables is intended and the inspection not explicitly disabled

Also, astropy and ccdproc have some interesting quirks, especially when it comes to reading fits files. Saving them, 
changing them with astropy facilites and re-saving them often fails, so a bunch of weird roundtrips had to be made.
See comments containing e.g. "WTF"

In case this sees further development there would be a bunch of opportunities for refactoring to make this easier:
 * In case you want to add another instrument, first unifiy the file IO with the classifier (for now the file is read twice in some cases)
  and then extract all necessary header-keywords to create a dataformat that can be fed to the reduction toolchain regardles of source
  
 * A cleaner separation of IO and in-memory data would make maintenance easier, especially the astromatic interface
 
 * I'm not exactly happy with the way the cli is looking now, it's quite a lot that you need to specify explicitly and
 a lot of possible errors when specifying arguments only cause trouble after a few seconds. It might be cleaner to first
 focus on making this a useful library to use interactively and then maybe switch to using it from short scripts.
 Another approach might be to have a configuration file that can override defaults on a per-folder basis so you
  don't have to remember/type everything again.  




