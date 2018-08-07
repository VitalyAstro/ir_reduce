import subprocess as sp
import os
import tempfile
from typing import Union, Tuple, List, Dict
from astropy.nddata.ccddata import CCDData
import astropy.io.fits as fits
import sys
import shutil

"""
Throughout this file: sex->SourceExtractor
"""
this_dir, this_file = os.path.split(__file__)


class Config:
    """
    a helper class to bundle parameters for scamp/sextractor

    TODO: maybe allow to override parameters from the config files here with an "additional params"-entry
    and pass them like "sex -MYPARAM MYVAL"
    """

    def __init__(self):
        self.sextractor_param = os.path.join(this_dir, 'default.param')
        self.sextractor_config = os.path.join(this_dir, 'sex.config')
        self.scamp_config = os.path.join(this_dir, 'scamp.config')
        self.sextractor_outfile = 'sexout.fits'
        self.sex_cmd = 'sex'
        self.scamp_cmd = 'scamp'

    @staticmethod
    def default():
        return Config()


def astroreff_files(input_files: List[str], config: Config = Config.default()) -> None:
    """
    Runs SExtractor and scamp on the given files to astroreference
    :param input_files: List of files to astroreference
    :param config: configuration object for scamp/sextractor
    :return: None, will write header/wcs to files
    """
    for file in input_files:
        astroref_file(file, file + '_astroreff', config=config)


def astroref_file(input_path: str, output_path: str, config: Config = Config.default()) -> str:
    """

    :param input_path:
    :param output_path:
    :param config: configuration object for scamp/sextractor
    :return:
    """
    input_path = os.path.abspath(input_path)
    output_path.replace('.fits', '')
    ouput_path = os.path.abspath(output_path)

    input_data = CCDData.read(input_path)

    scamp_data, sextractor_data = run_astroref(input_data, config=config)

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


def parse_key_val_config(config: str) -> Dict[str, str]:
    """
    :param config: configuration object to validate
    :return: True if valid, false otherwise
    """
    import re
    lines = config.splitlines()
    lines = [re.sub(r'#.*', '', line) for line in lines]  # get rid of everything after '#'
    ret = dict()
    for line in lines:
        if line.strip() == '':
            continue
        try:
            key, value = re.split(r'\s+', line.strip())
            ret[key] = value
        except ValueError as err:
            if 'values to unpack' in str(err):
                print('Got ambiguous line: ', line)
            else:
                raise
    return ret


def is_config_valid(config: Config) -> bool:
    """
    This function verifies that a config object is valid/sensible
    """
    with open(config.sextractor_config) as f:
        sex_cfg = parse_key_val_config(f.read())
    # with open(config.scamp_config) as f: # don't need this yet
    #    scamp_cfg = parse_key_val_config(f.read())

    valid = config.sextractor_outfile == sex_cfg['CATALOG_NAME'] and \
            sex_cfg['CATALOG_TYPE'] == 'FITS_LDAC' and \
            sex_cfg['HEADER_SUFFIX'] == '.head'

    return valid


def run_astroref(input_data: Union[str, CCDData], config: Config = Config.default(), working_dir: str = '',
                 verbose: int = 1) -> Tuple[str, bytes]:
    """
    TODO maybe wrapper that writes out strings and CCDData to files so that this function can only work with FS data

    :param input_data:
    :param config:
    :param working_dir:
    :param verbose:
    :return: tuple(scamp_data, sextractor_data)
    """

    if not is_config_valid(config):
        raise ValueError()

    tmpdir_pin = tempfile.TemporaryDirectory()
    working_dir = working_dir if working_dir else tmpdir_pin.name  # gets deleted automatically
    shutil.copy(config.sextractor_param, working_dir)
    open('default.conv', 'a').close()  # touch #TODO make configurable? Convolves image in sextractor with filter

    if isinstance(input_data, CCDData):
        fname = os.path.join(working_dir, 'sextractorInput.fits')
        input_data.write(fname, overwrite=True)
    else:
        fname = os.path.abspath(input_data)

    sex_process = sp.run([config.sex_cmd, fname, '-c', config.sextractor_config], cwd=working_dir, stdout=sp.PIPE,
                         stderr=sp.PIPE,
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

    scamp_process = sp.run([config.scamp_cmd, config.sextractor_outfile, '-c', config.scamp_config], cwd=working_dir,
                           stdout=sp.PIPE, stderr=sp.PIPE,
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
    # SExtractor will write to CATALOG_NAME (sextractor config)
    # by HEADER_SUFFIX in its config scamp will write its output to sextractor_outfile but fits->head
    with open(os.path.join(working_dir, config.sextractor_outfile.replace('.fits', '.head'))) as scamp_outfile:
        scamp_data = scamp_outfile.read()
    with open(os.path.join(working_dir, config.sextractor_outfile), 'rb') as f:
        sextractor_data = f.read()

    return scamp_data, sextractor_data
