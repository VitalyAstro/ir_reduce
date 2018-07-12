import pytest
from textwrap import dedent
from unittest import mock
from .. import run_astroref, astroref_file, astroreff_all, parse_key_val_config

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


