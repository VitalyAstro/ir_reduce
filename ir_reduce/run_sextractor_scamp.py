import subprocess as sp
import os
import tempfile
from typing import Union, Tuple, List, Dict
from astropy.nddata.ccddata import CCDData
import astropy.io.fits as fits
import sys
import shutil
import logging
"""
Throughout this file: sex->SourceExtractor
"""
this_dir, this_file = os.path.split(__file__)


class Config:
    def __init__(self):
        self.sextractor_param: str = os.path.join(this_dir, 'default.param'),
        self.sextractor_config: str = os.path.join(this_dir, 'sex.config'),
        self.scamp_config: str = os.path.join(this_dir, 'scamp.config')
        self.sex_cmd = 'sex'
        self.scamp_cmd = 'scamp'

    @staticmethod
    def default():
        return Config()


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

    # So you could use update(**header). That would interpret the header as a dictionary, which does not work for
    # comment and History, as they can be present multiple times
    input_data.header.update(scamp_header)

    input_data.write(output_path + '.fits', overwrite=True)

    return scamp_data


def parse_key_val_config(input: str) -> Dict[str,str]:
    import re
    lines = input.splitlines()
    lines = [re.sub(r'#.*', '', line) for line in lines] # get rid of everything after '#'
    ret = dict()
    for line in lines:
        try:
            key, value = re.split(r'\s+', line.strip())
        except ValueError as err:
            if 'values to unpack' in err:
                logging.warning('Got ambigous line: ', line)
            else:
                raise
        ret[key] = value

def verify_configs(config: Config):
    """TODO: Verify that the IO-parameters in the config files of scamp and sextractor fit together"""
    with open(config.sextractor_config) as f:
        sex_cfg = parse_key_val_config(f.read())
    with open(config.scamp_config) as f:
        scamp_cfg = parse_key_val_config(f.read())




def run(input_data: Union[str, CCDData], config: Config = Config.default(), working_dir: str = '', verbose: int = 1) -> Tuple[str, bytes]:
    """
    TODO: maybe wrapper to call with configs received as string?

    :param input_data:
    :param config:
    :param working_dir:
    :param verbose:
    :return:
    """

    verify_configs(config)

    working_dir = working_dir if working_dir else tempfile.TemporaryDirectory() # gets deleted automatically
    shutil.copy(config.sextractor_param, working_dir)
    open('default.conv', 'a').close()  # touch #TODO make configurable

    if isinstance(input_data, CCDData):
        fname = os.path.join(working_dir, 'sextractorInput.fits')
        input_data.write(fname, overwrite=True)
    else:
        fname = os.path.abspath(input_data)

    sex_process = sp.run([config.sex_cmd, fname, '-c', config.sextractor_config], cwd=working_dir, stdout=sp.PIPE, stderr=sp.PIPE,
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
    scamp_process = sp.run([config.scamp_cmd, 'sexout.fits', '-c', config.scamp_config], cwd=working_dir, stdout=sp.PIPE, stderr=sp.PIPE,
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
    with open(os.path.join(working_dir, 'sexout.head')) as scamp_outfile:
        scamp_data = scamp_outfile.read()
    with open(os.path.join(working_dir, 'sexout.fits'), 'rb') as f:  # see name in scamp runner
        sextractor_data = f.read()


    return scamp_data, sextractor_data
