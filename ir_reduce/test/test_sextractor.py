import pytest
from textwrap import dedent
import tempfile
from unittest import mock
import os
from .. import run_astroref, astroref_file, astroreff_all, parse_key_val_config, is_config_valid, Config
from .. import sp


class TestConfig():
    """Offers a context manager that fills a config with empty tempfiles and deletes them after execution"""

    def __init__(self):
        _, self.sex_filename = tempfile.mkstemp()
        __, self.scamp_filename = tempfile.mkstemp()

        config = Config.default()
        config.sextractor_config = self.sex_filename
        config.scamp_config = self.scamp_filename
        self.config = config

        with open(config.sextractor_config , 'w') as f:
            f.write(dedent('''
            CATALOG_TYPE FITS_LDAC
            CATALOG_NAME sexout.fits 
            HEADER_SUFFIX .head
            '''))

    def __enter__(self):
        return self.config

    def __exit__(self, exc_type, exc_val, exc_tb):
        os.remove(self.sex_filename)
        os.remove(self.scamp_filename)

def recorder(*args, **kwargs):
    return args, kwargs

@pytest.mark.incremental
class TestRun:

    def test_parse_key_val_config(self, capsys):
        teststring=dedent("""         
          AHEADER_SUFFIX         .ahead          # Filename extension for additional
                                                 # input headers
          HEADER_SUFFIX   \t      .head           # Filename extension for output headers
           
          #------------------------------- Check-plots ----------------------------------
           
          CHECKPLOT_DEV    PNG             # NULL, XWIN, TK, PS, PSC, XFIG, PNG,
                                                 # JPEG, AQT, PDF or SVG
          CHECKPLOT_TYPE         FGROUPS,DISTORTION,ASTR_INTERROR2D,ASTR_INTERROR1D,ASTR_REFERROR2D,ASTR_REFERROR1D,ASTR_CHI2,PHOT_ERROR
            CHECKPLOT_NAME         fgroups,distort,astr_interror2d,astr_interror1d,astr_referror2d,astr_referror1d,astr_chi2,psphot_error # Check-plot filename(s)        
          """)
        badstring = dedent("""
        # Comment
         A B C
         A
         
        #Comment
        """)

        data = parse_key_val_config(teststring)
        assert data['CHECKPLOT_DEV'] == 'PNG'

        data = parse_key_val_config(badstring)
        captured = capsys.readouterr()
        assert 'Got ambiguous line' in captured.out



    def test_config_valid(self):
        with TestConfig() as valid_config:
            assert is_config_valid(valid_config)

        with TestConfig() as invalid_config:
            invalid_config.sextractor_outfile = "not the same as catalogue"
            with open(invalid_config.sextractor_config, 'w') as f:
                f.write(dedent('''
                CATALOG_TYPE FITS_LDAC
                CATALOG_NAME sexout.fits 
                HEADER_SUFFIX .head
                '''))
            assert not is_config_valid(invalid_config)

        with TestConfig() as invalid_config:
            with open(invalid_config.sextractor_config, 'w') as f:
                f.write(dedent('''
                CATALOG_TYPE FITS_LDAC
                CATALOG_NAME sexout.fits 
                HEADER_SUFFIX .Not_head
                '''))
            assert not is_config_valid(invalid_config)

        with TestConfig() as invalid_config:
            with open(invalid_config.sextractor_config, 'w') as f:
                f.write(dedent('''
                CATALOG_TYPE NOT_FITS_LDAC
                CATALOG_NAME sexout.fits 
                HEADER_SUFFIX .head
                '''))
            assert not is_config_valid(invalid_config)



    def test_run_with_fake_subprocess(self):
        with mock.patch('subprocess.run', recorder), TestConfig() as config:
            scamp_data, sex_data = run_astroref('dummyFilename', config)
            assert '' == scamp_data
            assert '' == sex_data

    @pytest.mark.integration #TODO mark for "need echo present"
    def test_run_with_fake_binaries(self):
        pass

    @pytest.mark.integration #TODO not sure if this is the right mark for network acces+Data needed
    def test_run_with_real_binaries(self):
        pass

