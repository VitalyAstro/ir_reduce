import os
from fnmatch import fnmatch
from collections import namedtuple

# from astropy.io.fits import Header
from astropy.io import fits

from .image_type_classifier import image_category, Category

ImageGroup = namedtuple('ImageGroup', ['bad', 'flat', 'images'])
fits_match = '*.[Ff][Ii][Tt][Ss]'


def discover_filename(directory: str) -> ImageGroup:
    """
    find all files in a given directory that look like exposures, bad-pixel maps and flat fields
    :param directory:
    :return: Named tuple ImageGroup, contains lists of detected files
    """
    # This is pretty basic matching so far
    bad_match = '*[Bb][Aa][Dd]*'
    flat_match = '*[Ff][Ll][Aa][Tt]*'

    fits_files = {os.path.join(directory, file) for file in os.listdir(directory) if fnmatch(file, fits_match)}

    # everything with 'bad' in it is a bad pixel mask, everything with 'flat' is a flat field
    bad_candidates = {file for file in fits_files if fnmatch(file, bad_match)}
    flat_candidates = {file for file in fits_files if fnmatch(file, flat_match)}
    # flat and bad can't overlap...
    assert (len(bad_candidates.intersection(flat_candidates)) == 0)

    # everything else must be data
    image_files = fits_files.difference(bad_candidates, flat_candidates)

    return ImageGroup(bad=bad_candidates, flat=flat_candidates, images=image_files)


def discover_header(directory: str) -> ImageGroup:

    """
    Sort images based on header information
    :param directory: find fits-files where?
    :return: Named tuple ImageGroup, contains lists of detected files
    """
    # This would be a little less duplication if everything in main.py worked with CCDData directly and the IO was
    # factored out.

    fits_filenames = [os.path.join(directory, file) for file in os.listdir(directory) if fnmatch(file, fits_match)]
    # TODO Header.fromfile seems to crap out sometimes. not sure if this is a bug
    # category = [image_category(Header.fromfile(fname)) for fname in fits_filenames]
    category = [image_category(fits.open(fname)[0].header) for fname in fits_filenames]

    # TODO there's no way to find any bad pixel maps for ALFSOC because I don't know what the header would be
    # For now you need to manually change the header of the file so that IMAGETYP == 'BAD_PIXEL'
    # d = fits.open('bad_cold5.fits')
    # d[0].header['IMAGETYP'] = 'BAD_PIXEL'
    # d.writeto('bad_cold5_with_header_change.fits')
    bad = [fname for fname, cat in zip(fits_filenames, category) if cat == Category.BAD]
    flat = [fname for fname, cat in zip(fits_filenames, category) if cat == Category.FLAT]
    images = [fname for fname, cat in zip(fits_filenames, category) if cat == Category.SCIENCE]

    return ImageGroup(bad=bad, flat=flat, images=images)







