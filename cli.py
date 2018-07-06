import argparse
import os
# import reduce
from typing import Iterable, Any

VERSION='0.1'

def call_reduce(bads: Iterable[str],
                flats: Iterable[str],
                images: Iterable[str],
                flags: argparse.Namespace) -> None:
    print(bads, flats, images)


def do_manual(args: argparse.Namespace):
    bads, flats, images = args.bad, args.flat, args.exposures
    return call_reduce(bads, flats, images, args)


def do_discover(args: argparse.Namespace):
    import imageDiscovery
    bads, flats, images = imageDiscovery.discover(args.folder)
    return call_reduce(bads, flats, images, args)

def do_nothing(args: Any) -> None:
    pass

parser = argparse.ArgumentParser(description='Reduction toolchain')

group = parser.add_mutually_exclusive_group()
group.add_argument('-m', '--median', action='store_true', help='combine images using median')
group.add_argument('-a', '--average', action='store_true', help='combine images using average')
parser.add_argument('-r', '--register-images', action='store_true',
                    help='images are aligned with cross correlation, not just based on WCS')
# Not sure if the next one is a good idea...
parser.add_argument('--force', '--javascript', action='store_true',
                    help='Non fatal errors and validation is ignored. https://www.destroyallsoftware.com/talks/wat')
parser.add_argument('--verbose', '-v', action='count')
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
sub_parser.add_argument('-c', '--confirm', help='Confirm file selection')
sub_parser.set_defaults(func=do_discover)


args = parser.parse_args()
print(args)
args.func(args)
