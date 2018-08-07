import pytest
from ir_reduce import cli_main, cli

def test_basic():
    cli_main()

def test_parsing():
    parser = cli.parser
    parser.parse_args(['out.fits', 'm', '-b', '../testdata/bad_*', '-f', '../testdata/FlatJ.fits', '-e', '../testdata/NCAc0708*fits'])

