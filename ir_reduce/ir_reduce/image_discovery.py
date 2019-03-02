import os
from fnmatch import fnmatch
from collections import namedtuple

ImageGroup = namedtuple('ImageGroup', ['bad', 'flat', 'images'])


def discover_filename(directory: str) -> ImageGroup:
    """
    find all files in a given directory that look like exposures, bad-pixel maps and flat fields
    :param directory:
    :return: Named tuple ImageGroup, contains lists of detected files
    """
    # This is pretty basic matching so far
    fits_match = '*.[Ff][Ii][Tt][Ss]'
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

    raise NotImplementedError("This would be a lot easier after having read the data")
    fits_files = {os.path.join(directory, file) for file in os.listdir(directory)}

