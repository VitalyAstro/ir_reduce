#!/usr/bin/env python3
import argparse
import os
import logging
import ir_reduce
from textwrap import dedent
from typing import Iterable, Any, Sequence

# todo tmp
logging.getLogger().setLevel(logging.DEBUG)

VERSION = '0.1'

output_default = 'reduced.fits'

def call_reduce(bads: Iterable[str],
                flats: Iterable[str],
                images: Iterable[str],
                flags: argparse.Namespace) -> None:
    ir_reduce.do_everything(bads, flats, images,
                            output=flags.output,
                            filter_letter=flags.filter[0],
                            combine='average' if flags.average else 'median',
                            skyscale_method='subtract' if flags.subtract else 'divide')
                            #register=flags.register_images,
                            #verbosity=flags.verbose,
                            #force=flags.force)

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

    return call_reduce(args.bad, args.flat, args.images, args)


def do_only_astroref(args: argparse.Namespace):
    args.images = extract_textfile_if_present(args.images)
    args.output = extract_textfile_if_present(args.output)

    if len(args.output) == 1 and args.output[0] == output_default and len(args.images):
        args.output = [base+'_astro_refferenced'+ext for base, ext in os.path.splitext(args.images)]
    if not len(args.output) == len(args.images):
        raise ValueError('Need the same amount of images and output filenames')

    ir_reduce.only_astroreff(args.images, args.output)


def do_discover(args: argparse.Namespace):
    from ir_reduce import image_discovery
    bads, flats, images = image_discovery.discover(args.folder)

    if args.verbose > 0 or args.confirm:
        logging.info(dedent(f"""\
        discovered the following files: Bad Pixel Maps: {bads}
        flat fields: {flats}
        exposures: {images}"""))
    if args.confirm:
        if input('Continue? [y/n]').lower() != 'y':
            logging.warning('Exiting...')
            exit(0)

    return call_reduce(bads, flats, images, args)


def do_nothing(args: Any) -> None:
    pass


parser = argparse.ArgumentParser(description='Reduction toolchain',formatter_class=argparse.ArgumentDefaultsHelpFormatter)

group = parser.add_mutually_exclusive_group()
group.add_argument('-m', '--median', action='store_true', default=True, help='combine images using median')
group.add_argument('-a', '--average', action='store_true', help='combine images using average')
group = parser.add_mutually_exclusive_group()
group.add_argument('-s', '--subtract', action='store_true', help='skyscale images by subtraction')
group.add_argument('-d', '--divide', action='store_true', default=True, help='skyscale images by division')
parser.add_argument('-r', '--register-images', action='store_true',
                    help='[not implemented] images are aligned with cross correlation, not just based on WCS')
parser.add_argument('--filter', '-fl', nargs=1, default='J', help='What image filter do we want to process?')

parser.add_argument('--verbose', '-v', action='count', default=0, help='No effect yet')
parser.add_argument('--version', action='version', version=VERSION)

parser.set_defaults(func=do_nothing)

subparsers = parser.add_subparsers(help='sub commands')

sub_parser = subparsers.add_parser('manual', aliases=['m'], help='Specify paths to images yourself')
sub_parser.add_argument('-f', '--flat', required=True, metavar='flatfield', nargs=1, type=str,
                        help='Flat field image. Can specify in textfile and pass @textfile')
sub_parser.add_argument('-b', '--bad', required=True, metavar='badPixelMap', nargs='+', type=str,
                        help='bad pixel maps. Will be combined. Can specify in textfile and pass @textfile')
sub_parser.add_argument('-i', '--images', required=True, metavar='image', nargs='+', type=str,
                        help='the images you want to combine. Can specify in textfile and pass @textfile')
sub_parser.add_argument('-o', '--output', nargs='?', type=str, default=output_default,
                        help='output file to write to, default: reduced.fits')
sub_parser.set_defaults(func=do_manual)

sub_parser = subparsers.add_parser('discover', aliases=['d'], help='Discover images in optionally specified directory')
sub_parser.add_argument('folder', nargs='?', type=str, default=os.getcwd(),
                        help='folder to search for files to analyze')
sub_parser.add_argument('-c', '--confirm', action='store_true', help='Confirm file selection')
sub_parser.add_argument('-o', '--output', nargs='?', type=str, default=output_default,
                        help='output file to write to, default: reduced.fits')
sub_parser.set_defaults(func=do_discover)

sub_parser = subparsers.add_parser('astroref', aliases=['ref'],
                                   help='only perform astrorefferencing with sextractor/scamp on already reduced image')
sub_parser.add_argument('-i', '--images', metavar='images', nargs='+', type=str,
                        help='image(s) to astroreff. Can use @textfile')
sub_parser.add_argument('-o', '--output', nargs='+', type=str, default=[output_default],
                        help='output file(s) to write to, default: reduced.fits, can use @textfile')
sub_parser.set_defaults(func=do_only_astroref)

def cli_main():
    args = parser.parse_args()
    args.func(args)

if __name__=="__main__":
    cli_main()
