import subprocess as sp
import os
import tempfile
from typing import Union, Tuple
from astropy.nddata.ccddata import CCDData
import astropy.io.fits as fits
import sys
import shutil
from io import StringIO

this_dir, this_file = os.path.split(__file__)

sextractor = 'sex'
scamp = 'scamp'

sextractor_config = os.path.join(this_dir, 'sex.config')
sextractor_param = os.path.join(this_dir, 'default.param')
scamp_config = os.path.join(this_dir, 'scamp.config')



def run(input_data: Union[str, CCDData], verbose: int = 1) -> Tuple[str,bytes]:
    with tempfile.TemporaryDirectory() as tmpdir:
        #tmpdir = '/home/basti/NTE/tmp' #TODO hacks for debugging
        shutil.copy(sextractor_param, tmpdir)
        open('default.conv', 'a').close() #touch

        if isinstance(input_data, CCDData):
            fname = os.path.join(tmpdir, 'sextractorInput.fits')
            input_data.write(fname, overwrite=True)
        else:
            fname = input_data

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

        with open(os.path.join(tmpdir,'sexout.head')) as scamp_outfile:
            scamp_data = scamp_outfile.read()
        with open(os.path.join(tmpdir,'sexout.fits'), 'rb') as f: #see name in scamp runner
            sextractor_data = f.read()


    return scamp_data, sextractor_data
