import argparse
import os
parser = argparse.ArgumentParser(description='Reduction toolchain')

group=parser.add_mutually_exclusive_group()
group.add_argument('-m', '--median', action='store_true', help='combine images using median')
group.add_argument('-a', '--average', action='store_true', help='combine images using average')

parser.add_argument('-r', '--register-images', action='store_true',
                    help='images are aligned with cross correlation, not just based on WCS')

subparsers = parser.add_subparsers(help='sub commands')

sparser = subparsers.add_parser('manual', aliases=['m'], help='Specify paths to images yourself')
sparser.add_argument('-f', '--flat', required=True, metavar='flatfield', nargs=1, type=str,
                    help='Flat field image')
sparser.add_argument('-b', '--bad', required=True, metavar='badPixelMap', nargs='+', type=str,
                     help='bad pixel maps. Will be combined')
sparser.add_argument('-e', '--exposures', required=True, metavar='image', nargs='+', type=str,
                     help='the images you want to combine')


sparser = subparsers.add_parser('discover', aliases=['d'], help='Discover images in optionally specified directory')
sparser.add_argument('folder', nargs='?', type=str, default=os.getcwd(),
                     help='folder to search for files to analyze')


print(parser.parse_args())
