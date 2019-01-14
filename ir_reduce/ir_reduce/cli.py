#!/usr/bin/env python3
import argparse
import logging
import os
from textwrap import dedent
from typing import Iterable, Any, Sequence
import ir_reduce

import ir_reduce.run_sextractor_scamp

# todo tmp
logging.getLogger().setLevel(logging.DEBUG)

VERSION = '0.1'

output_default = 'reduced.fits'


def astroref_and_or_reduce(bads: Iterable[str],
                           flats: Iterable[str],
                           images: Iterable[str],
                           flags: argparse.Namespace,
                           astromatic_cfg: ir_reduce.run_sextractor_scamp.Config) -> None:
    if flags.no_ref:
        to_call = ir_reduce.do_only_reduce
    else:
        to_call = ir_reduce.do_everything

    to_call(bads, flats, images,
            output=flags.output,
            filter_letter=flags.filter[0],
            combine='average' if flags.average else 'median',
            skyscale_method='subtract' if flags.subtract else 'divide',
            astromatic_cfg=astromatic_cfg)
    # register=flags.register_images,
    # verbosity=flags.verbose,
    # force=flags.force)


def extract_textfile_if_present(arguments: Sequence[str]):
    """slightly hacky way to implement @list syntax"""
    if any('@' in arg for arg in arguments):
        if not len(arguments) == 1:
            raise ValueError('When using @listfile syntax, you must specify exactly one argument')
        with open(arguments[0].replace('@', ''), 'r') as f:
            # remove whitespaces, empty lines and '#' comments
            arguments = [i.strip() for i in f.readlines() if i.strip() and not i.strip().startswith('#')]

    return [os.path.abspath(arg) for arg in arguments]


def do_manual(args: argparse.Namespace):
    args.images = extract_textfile_if_present(args.images)
    args.bad = extract_textfile_if_present(args.bad)
    args.flat = extract_textfile_if_present(args.flat)

    astromatic_cfg = parse_astromatic_config(args)

    return astroref_and_or_reduce(args.bad, args.flat, args.images, args, astromatic_cfg)


def do_only_astroref(args: argparse.Namespace):
    args.images = extract_textfile_if_present(args.images)
    args.output = extract_textfile_if_present(args.output)

    if len(args.output) == 1 and args.output[0] == output_default and len(args.images):
        # noinspection PyTypeChecker
        args.output = [base + '_astro_refferenced' + ext for base, ext in os.path.splitext(args.images)]
    if not len(args.output) == len(args.images):
        raise ValueError('Need the same amount of images and output filenames')

    astromatic_cfg = parse_astromatic_config(args)

    ir_reduce.do_only_astroref(args.images, args.output, astromatic_cfg)


def do_discover(args: argparse.Namespace):
    from ir_reduce import image_discovery
    bads, flats, images = image_discovery.discover(args.folder)

    if len(bads) == 0:
        raise ValueError('No bad pixel map found')
    if len(flats) == 0:
        raise ValueError('No flatfield found')
    if len(images) == 0:
        raise ValueError('No images found')

    if args.verbose > 0 or args.confirm:
        logging.info(dedent(f"""\
        discovered the following files: Bad Pixel Maps: {bads}
        flat fields: {flats}
        exposures: {images}"""))
    if args.confirm:
        if input('Continue? [y/n]').lower() != 'y':
            logging.warning('Exiting...')
            exit(0)

    astromatic_cfg = parse_astromatic_config(args)

    return astroref_and_or_reduce(bads, flats, images, args, astromatic_cfg)


def do_transient_detection(args: argparse.Namespace):
    from ir_reduce.transient_detection import transient_detection

    return transient_detection(args.sexout, args.refcat, args.image)


def do_nothing(*_: Any) -> None:
    pass


def parse_astromatic_config(args: argparse.Namespace) -> ir_reduce.run_sextractor_scamp.Config:
    cfg = ir_reduce.run_sextractor_scamp.Config.default()

    for filelist in (args.sextractor_config, args.sextractor_params, args.scamp_config):
        if not os.path.exists(filelist[0]):
            raise ValueError("File "+filelist[0]+" not found")

    cfg.sextractor_config = os.path.abspath(args.sextractor_config[0])
    cfg.sextractor_params = os.path.abspath(args.sextractor_params[0])
    cfg.scamp_config = os.path.abspath(args.scamp_config[0])
    cfg.working_dir = os.path.abspath(args.wdir[0])
    cfg.scamp_overrides = args.scamp_overrides
    cfg.sextractor_overrides = args.sextractor_overrides


    return cfg



parser = argparse.ArgumentParser(description='Reduction toolchain',
                                 formatter_class=argparse.ArgumentDefaultsHelpFormatter)

group = parser.add_mutually_exclusive_group()
group.add_argument('-m', '--median', action='store_true', default=True, help='combine images using median')
group.add_argument('-a', '--average', action='store_true', help='combine images using average')
group = parser.add_mutually_exclusive_group()
group.add_argument('-s', '--subtract', action='store_true', help='skyscale images by subtraction')
group.add_argument('-d', '--divide', action='store_true', default=True, help='skyscale images by division')
parser.add_argument('-r', '--register-images', action='store_true',
                    help='[not implemented] images are aligned with cross correlation, not just based on WCS')
parser.add_argument('--filter', '-fl', nargs=1, default='J', help='What image filter do we want to process?')
parser.add_argument('--no-ref', '-n', action='store_true', default=False,
                    help='the output image won\'t be astroreferenced')

parser.add_argument('--verbose', '-v', action='count', default=0, help='No effect yet')
parser.add_argument('--version', action='version', version=VERSION)

parser.set_defaults(func=do_nothing)

def add_astromatic_params(parser):
    astromatic_cfg = ir_reduce.run_sextractor_scamp.Config.default()
    parser.add_argument('--sextractor-config','-sexc', nargs=1, type=str, default=[astromatic_cfg.sextractor_config],
                        help='override inbuilt source extractor config file')
    parser.add_argument('--sextractor-params','-sexp', nargs=1, type=str, default=[astromatic_cfg.sextractor_param],
                        help='override inbuilt source extractor parameter file')
    parser.add_argument('--scamp-config', '-sconf', nargs=1, type=str, default=[astromatic_cfg.scamp_config],
                        help='override inbuilt scamp config file')
    parser.add_argument('--wdir', '-wd', nargs=1, default=[astromatic_cfg.working_dir],
                        help='working directory for scamp/sextractor if you want to keep intermediate files')
    parser.add_argument('--scamp-overrides', '-sco', nargs='+', default=astromatic_cfg.scamp_overrides, type=str,
                        help='override configuration values for scamp as "KEY0=VAL0 KEY1=VAL1"')
    parser.add_argument('--sextractor-overrides', '-sexo', nargs='+',
                        default=astromatic_cfg.sextractor_overrides, type=str,
                        help='override configuration values for source extractor as "KEY0=VAL0 KEY1=VAL1"')

sub_parsers = parser.add_subparsers(title='subcommands', description='', help='sub commands')

sub_parser = sub_parsers.add_parser('manual', aliases=['m'], help='Specify paths to images yourself')
sub_parser.add_argument('-f', '--flat', required=True, metavar='flatfield', nargs='+', type=str,
                        help='Flat field image. Can specify in textfile and pass @textfile')
sub_parser.add_argument('-b', '--bad', required=True, metavar='badPixelMap', nargs='+', type=str,
                        help='bad pixel maps. Will be combined. Can specify in textfile and pass @textfile')
sub_parser.add_argument('-i', '--images', required=True, metavar='image', nargs='+', type=str,
                        help='the images you want to combine. Can specify in textfile and pass @textfile')
sub_parser.add_argument('-o', '--output', nargs='?', type=str, default=output_default,
                        help='output file to write to, default: reduced.fits')
add_astromatic_params(sub_parser)
sub_parser.set_defaults(func=do_manual)

sub_parser = sub_parsers.add_parser('discover', aliases=['d'], help='Discover images in optionally specified directory')
sub_parser.add_argument('folder', nargs='?', type=str, default=os.getcwd(),
                        help='folder to search for files to analyze')
sub_parser.add_argument('-c', '--confirm', action='store_true', help='Confirm file selection')
sub_parser.add_argument('-o', '--output', nargs='?', type=str, default=output_default,
                        help='output file to write to, default: reduced.fits')
add_astromatic_params(sub_parser)
sub_parser.set_defaults(func=do_discover)

sub_parser = sub_parsers.add_parser('astroref', aliases=['ref'],
                                    help='only perform astrorefferencing with sextractor/scamp on already reduced image')
sub_parser.add_argument('-i', '--images', metavar='images', nargs='+', type=str,
                        help='image(s) to astroreff. Can use @textfile')
sub_parser.add_argument('-o', '--output', nargs='+', type=str, default=[output_default],
                        help='output file(s) to write to, default: reduced.fits, can use @textfile')
add_astromatic_params(sub_parser)
sub_parser.set_defaults(func=do_only_astroref)

sub_parser = sub_parsers.add_parser('transient', aliases=['t'],
                                    help='use a reduced and astroreferenced image, source extractor output and'
                                         ' scamp reference cataloge to find divergences')
sub_parser.add_argument('image')
sub_parser.add_argument('sexout')
sub_parser.add_argument('refcat')
sub_parser.set_defaults(func=do_transient_detection)


# sub_parser = sub_parsers.add_parser('transient', aliases=['t'], help='perform some transient detection by comparing reduced image to reference catalogue')


def cli_main():
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    cli_main()
