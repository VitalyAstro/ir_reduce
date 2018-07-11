import subprocess as sp
import os
import tempfile
from typing import Union, Tuple, List
from astropy.nddata.ccddata import CCDData
import astropy.io.fits as fits
import sys
import shutil

this_dir, this_file = os.path.split(__file__)

sextractor = 'sex'
scamp = 'scamp'

sextractor_config = os.path.join(this_dir, 'sex.config')
sextractor_param = os.path.join(this_dir, 'default.param')
scamp_config = os.path.join(this_dir, 'scamp.config')


def astroreff_all(inputFiles: List[str]) -> None:
    for file in inputFiles:
        astroref_file(file, file + '_astroreff')


def astroref_file(input_path: str, output_path: str) -> str:
    input_path = os.path.abspath(input_path)
    output_path.replace('.fits', '')
    ouput_path = os.path.abspath(output_path)

    input_data = CCDData.read(input_path)

    scamp_data, sextractor_data = run(input_data)

    with open(ouput_path + 'scamp.head', 'w') as f:
        f.write(scamp_data)
    with open(ouput_path + '_sextractor.fits', 'wb') as f:
        f.write(sextractor_data)

    scamp_header = fits.Header.fromstring(scamp_data, sep='\n')

    # TODO cant write without this, scamp value does not work with fitsio
    # scamp_header["COMMENT"] = "No comment"
    # scamp_header["HISTORY"] = "NO HISTORY"
    input_data.header.update(scamp_header)

    input_data.write(output_path + '.fits', overwrite=True)

    return scamp_data


def run(input_data: Union[str, CCDData], sextractor_param=sextractor_param, sextractor_config=sextractor_config,
        scamp_config=scamp_config, verbose: int = 1) -> Tuple[str, bytes]:
    with tempfile.TemporaryDirectory() as tmpdir:
        # tmpdir = '/home/basti/NTE/tmp' #TODO hacks for debugging
        shutil.copy(sextractor_param, tmpdir)
        open('default.conv', 'a').close()  # touch

        if isinstance(input_data, CCDData):
            fname = os.path.join(tmpdir, 'sextractorInput.fits')
            input_data.write(fname, overwrite=True)
        else:
            fname = os.path.abspath(input_data)

        sex_process = sp.run([sextractor, fname, '-c', sextractor_config], cwd=tmpdir, stdout=sp.PIPE, stderr=sp.PIPE,
                             universal_newlines=True, timeout=30)
        if sex_process.returncode != 0:
            raise RuntimeError(
                f'''Sextractor failed to run
                args:
                {sex_process.args}
                stderr:
                {sex_process.stderr}
                stdout:
                {sex_process.stdout}''')
        elif verbose:
            print(sex_process.stdout)
            print(sex_process.stderr, file=sys.stdout)

        # todo output hardcoded. write to config file?
        scamp_process = sp.run([scamp, 'sexout.fits', '-c', scamp_config], cwd=tmpdir, stdout=sp.PIPE, stderr=sp.PIPE,
                               universal_newlines=True, timeout=30)
        if scamp_process.returncode != 0:
            raise RuntimeError(
                f'''Scamp failed to run
                args:
                {sex_process.args}
                stderr:
                {scamp_process.stderr}
                stdout:
                {scamp_process.stdout}''')
        elif verbose:
            print(scamp_process.stdout)
            print(scamp_process.stderr, file=sys.stdout)

        scamp_data, sextractor_data = None, None
        with open(os.path.join(tmpdir, 'sexout.head')) as scamp_outfile:
            scamp_data = scamp_outfile.read()
        with open(os.path.join(tmpdir, 'sexout.fits'), 'rb') as f:  # see name in scamp runner
            sextractor_data = f.read()

    return scamp_data, sextractor_data
