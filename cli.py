#!/usr/bin/env python3
import argparse
import os
import logging
import ir_reduce
from textwrap import dedent
from typing import Iterable, Any

# todo tmp
logging.getLogger().setLevel(logging.DEBUG)

VERSION = '0.1'


def call_reduce(bads: Iterable[str],
                flats: Iterable[str],
                images: Iterable[str],
                flags: argparse.Namespace) -> None:
    ir_reduce.do_everything(bads, flats, images,
                            output=flags.output,
                            filter=flags.filter[0],
                            combine='average' if flags.average else 'median',
                            skyscale_method='subtract' if flags.subtract else 'divide',
                            register=flags.register_images,
                            verbosity=flags.verbose,
                            force=flags.force)


def do_manual(args: argparse.Namespace):
    return call_reduce(args.bad, args.flat, args.exposures, args)


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

# Not sure if the next one is a good idea...
parser.add_argument('--force', '--javascript', action='store_true',
                    help='[not implemented] Non fatal errors and validation are ignored. https://www.destroyallsoftware.com/talks/wat')
parser.add_argument('output', nargs='?', type=str, default='reduced.fits',
                        help='output file to write to, default: reduced.fits')

parser.add_argument('--verbose', '-v', action='count', default=0)
parser.add_argument('--version', action='version', version=VERSION)

parser.set_defaults(func=do_nothing)

subparsers = parser.add_subparsers(help='sub commands')

sub_parser = subparsers.add_parser('manual', aliases=['m'], help='Specify paths to images yourself')
sub_parser.add_argument('-f', '--flat', required=True, metavar='flatfield', nargs=1, type=str,
                        help='Flat field image')
sub_parser.add_argument('-b', '--bad', required=True, metavar='badPixelMap', nargs='+', type=str,
                        help='bad pixel maps. Will be combined')
sub_parser.add_argument('-e', '--exposures', required=True, metavar='image', nargs='+', type=str,
                        help='the images you want to combine')
sub_parser.set_defaults(func=do_manual)

sub_parser = subparsers.add_parser('discover', aliases=['d'], help='Discover images in optionally specified directory')
sub_parser.add_argument('folder', nargs='?', type=str, default=os.getcwd(),
                        help='folder to search for files to analyze')
sub_parser.add_argument('-c', '--confirm', action='store_true', help='Confirm file selection')
sub_parser.set_defaults(func=do_discover)

args = parser.parse_args()
print(args)
args.func(args)
