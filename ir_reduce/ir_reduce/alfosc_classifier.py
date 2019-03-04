from .classifier_common import Band, Category
from astropy.io.fits import Header
import logging

image_category_str = 'IMAGECAT'
image_type = 'IMAGETYP'

# snippet to get an overview of a bunch of headers by making a pandas dataframe out of it
# datas = [CCDData.read(i) for i in glob.glob('*.fits')]
# heads = pd.DataFrame.from_records([i.header for i in datas])
# # these are the columns interesting for the band-function
# filter_col = [col for col in heads if col.startswith('AL') or col.startswith('FAF')]
# heads[filter_col]


def image_category(header: Header) -> Category:
    try:
        cat = header[image_category_str]
        img_type = header[image_type]
    except KeyError:
        logging.warning('could not determine image category')
        return Category.UNKNOWN

    if cat.strip() == '' and header['OBS_TYPE'] == 'IMAGING':
        return Category.SCIENCE
    elif img_type == 'BAD_PIXEL':
        return Category.BAD
    elif cat == 'CALIB' and 'FLAT' in img_type:
        return Category.FLAT
    elif cat == 'CALIB' and 'BIAS' in img_type:
        return Category.BIAS
    elif cat == 'TECHNICAL':
        return Category.TECHNICAL
    else:
        logging.warning('could not determine image category')
        return Category.UNKNOWN


def band(header: Header) -> Band:
    # ALFTID, ALFTPOS, ALFTNM refer to the same thing, like for
    f_filter = header['ALFLTNM']
    fa_filter = header['FAFLTNM']
    grism = header['ALGRNM']

    assert sum('Open' in name for name in (f_filter, fa_filter, grism)) == 2, f'more than one filter selected: ' \
                                                                              f'{f_filter}, {fa_filter}, {grism}'

    filter_name = [name for name in (f_filter, fa_filter, grism) if 'Open' not in name][0]
    return Band.lookup(filter_name)


