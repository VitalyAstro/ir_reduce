import pytest
from textwrap import dedent
import tempfile
from unittest import mock
import os
import shutil
from ir_reduce import run_astroref, parse_key_val_config, is_config_valid, Config  # todo: astroref_file, astroreff_files


class ConfigForTest:
    """Offers a context manager that fills a config with empty tempfiles and deletes them after execution"""

    def __init__(self):
        _, self.sex_filename = tempfile.mkstemp()
        __, self.scamp_filename = tempfile.mkstemp()

        config = Config.default()
        config.sextractor_config = self.sex_filename
        config.scamp_config = self.scamp_filename
        self.config = config

        with open(config.sextractor_config, 'w') as f:
            f.write(dedent('''
            CATALOG_TYPE FITS_LDAC
            CATALOG_NAME sexout.fits 
            HEADER_SUFFIX .head
            '''))

        with open(config.scamp_config, 'w') as f:
            f.write(dedent('''
            CATALOG_NAME sexout.fits
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
        teststring = dedent("""         
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
        assert not data
        captured = capsys.readouterr()
        assert 'Got ambiguous line' in captured.out

    def test_config_valid(self):
        with ConfigForTest() as valid_config:
            assert is_config_valid(valid_config)

        with ConfigForTest() as invalid_config:
            invalid_config.sextractor_outfile = "not the same as catalogue"
            with open(invalid_config.sextractor_config, 'w') as f:
                f.write(dedent('''
                CATALOG_TYPE FITS_LDAC
                CATALOG_NAME sexout.fits
                HEADER_SUFFIX .head
                '''))
            assert not is_config_valid(invalid_config)

        with ConfigForTest() as invalid_config:
            with open(invalid_config.sextractor_config, 'w') as f:
                f.write(dedent('''
                CATALOG_TYPE FITS_LDAC
                CATALOG_NAME sexout.fits
                HEADER_SUFFIX .Not_head
                '''))
            assert not is_config_valid(invalid_config)

        with ConfigForTest() as invalid_config:
            with open(invalid_config.sextractor_config, 'w') as f:
                f.write(dedent('''
                CATALOG_TYPE NOT_FITS_LDAC
                CATALOG_NAME sexout.fits 
                HEADER_SUFFIX .head
                '''))
            assert not is_config_valid(invalid_config)

    def test_run_with_fake_subprocess(self):
        mock_run = mock.Mock()
        mock_process = mock.Mock  # this needs to be instantiated so /not/ mock.Mock()

        with mock.patch('subprocess.run', mock_run), ConfigForTest() as config, tempfile.TemporaryDirectory() as tmpdir:
            # mock/file setup
            mock_run.run.return_value = mock_process
            mock_process.returncode = 0

            config.working_dir = tmpdir

            with open(os.path.join(tmpdir, config.sextractor_outfile), 'w') as sexout:
                sexout.write('foo')
            with open(os.path.join(tmpdir, config.sextractor_outfile.replace('.fits', '.head')), 'w') as scampout:
                scampout.write('bar')
            open(os.path.join(tmpdir, 'foo.cat'), 'ab').close()
            # test run
            scamp_data, sex_data, reference_cat_data = run_astroref('dummyFilename', config)
            assert 'bar' == scamp_data
            assert b'foo' == sex_data

    def test_echo_present(self):
        assert shutil.which('echo')

    @pytest.mark.integration  # TODO mark for "need echo present"
    def test_run_with_fake_binaries(self):
        pass

    @pytest.mark.integration  # TODO not sure if this is the right mark for network access+testdata needed
    def test_run_with_real_binaries(self):
        pass
