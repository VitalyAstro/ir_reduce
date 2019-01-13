import pytest
from ir_reduce import cli_main, cli
from unittest import mock
import argparse
import tempfile
import os

def test_basic():
    # if --runintegration is passed to pytest, it polutes sys.argv
    import sys
    saved = sys.argv
    try:
        sys.argv = []
        cli_main()
    finally:
        sys.argv = saved

def test_parsing():
    parser = cli.parser
    parser.parse_args(['m', '-o', 'out.fits', '-b', '../testdata/bad_*', '-f', '../testdata/FlatJ.fits', '-i', '../testdata/NCAc0708*fits'])
    parser.parse_args(['m', '--output', 'out.fits', '-b', '../testdata/bad_*', '-f', '../testdata/FlatJ.fits', '-i', '../testdata/NCAc0708*fits'])

def test_roundtrip():
    parser = cli.parser
    # manual
    args = parser.parse_args(['m', '-o','out.fits', '-b', 'bad1', '-f', 'flat1', '-i', 'im1'])
    assert args.func == cli.do_manual
    mock_reduce = mock.Mock()
    with mock.patch('ir_reduce.cli.astroref_and_or_reduce', mock_reduce):
        args.func(args)

    mock_reduce.assert_called()

    # discover
    args = parser.parse_args(['d', '-o', 'out.fits', 'mydir'])
    assert args.func == cli.do_discover
    mock_reduce, mock_discover = mock.Mock(), mock.Mock()
    with mock.patch('ir_reduce.cli.astroref_and_or_reduce', mock_reduce), mock.patch('ir_reduce.image_discovery.discover', mock_discover):
        mock_discover.return_value = (1, 2, 3)
        args.func(args)

    mock_discover.assert_called()
    mock_reduce.assert_called()

def test_invalid_args(capsys):
    parser = cli.parser
    with pytest.raises(SystemExit):
        args = parser.parse_args(['m', '-o', 'out.fits', '-b'])
    captured = capsys.readouterr()
    assert 'manual: error: argument -b/--bad: expected at least one argument' in captured.err

def test_at_syntax():
    parser = cli.parser
    args = parser.parse_args(['m', '-o', 'out.fits', '-b', '@1', '@2', '-f', 'foo', '-i', 'bar'])
    # check if multiple @-args fail
    with pytest.raises(ValueError):
        args.func(args)

    with tempfile.TemporaryDirectory() as dir:
        bad, flat, im = [os.path.join(dir, i) for i in ('bad', 'flat', 'im')]
        with open(bad, 'w') as f:
            f.write('bad\nbar\n')
        with open(flat, 'w') as f:
            f.write('flat\nfoo\n')
        with open(im, 'w') as f:
            f.write('im\nbaz\n')
        args = parser.parse_args(['m', '-o', 'out.fits', '-b', f'@{bad}', '-f', f'@{flat}', '-i', f'@{im}'])

        mock_reduce = mock.Mock()
        with mock.patch('ir_reduce.cli.astroref_and_or_reduce', mock_reduce):
            args.func(args)
        absp = os.path.abspath
        mock_reduce.assert_called_with([absp('bad'), absp('bar')],
                                       [absp('flat'), absp('foo')],
                                       [absp('im'), absp('baz')], mock.ANY)



def test_astroref_only():
    parser = cli.parser
    args = parser.parse_args(['astroref', '-o', 'in.fits', 'in2.fits', '-i', 'out.fits', 'out.fits'])
    args = parser.parse_args(['astroref', '-i', 'in.fits', 'in2.fits', '-o', 'out.fits', 'out.fits'])
    args = parser.parse_args(['astroref', '-i', 'in.fits'])


    mock_aref = mock.Mock()
    with mock.patch('ir_reduce.do_only_astroref', mock_aref):
        args.func(args)

    mock_aref.assert_called_with([os.path.abspath('in.fits')], mock.ANY)

    args = parser.parse_args(['astroref', '-o', 'out.fits', '-i', 'a', 'b'])
    # check if mismatch between in/out arglength causes error
    with pytest.raises(ValueError):
        args.func(args)
