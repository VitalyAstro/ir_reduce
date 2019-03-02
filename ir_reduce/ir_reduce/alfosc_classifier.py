from .classifier_common import Band, Category
from astropy.nddata import CCDData

image_category_str = 'IMAGECAT'

# snippet to get an overview of a bunch of headers by making a pandas dataframe out of it
# datas = [CCDData.read(i) for i in glob.glob('*.fits')]
# heads = pd.DataFrame.from_records([i.header for i in datas])
# # these are the columns interesting for the band-function
# filter_col = [col for col in heads if col.startswith('AL') or col.startswith('FAF')]
# heads[filter_col]


def image_category(img: CCDData) -> Category:
    val = img.header[image_category_str]

    if val.strip() == '':
        return Category.SCIENCE
    elif val == 'CALIB':
        return Category.CALIBRATION
    elif val == 'TECHNICAL':
        return Category.TECHNICAL
    else:
        return Category.UNKNOWN


def band(img: CCDData) -> Band:
    # ALFTID, ALFTPOS, ALFTNM refer to the same thing, like for
    f_filter = img.header['ALFLTNM']
    fa_filter = img.header['FAFLTNM']
    grism = img.header['ALGRNM']

    assert sum('Open' in name for name in (f_filter, fa_filter, grism)) == 2, f'more than one filter selected: ' \
                                                                              f'{f_filter}, {fa_filter}, {grism}'

    filter_name = [name for name in (f_filter, fa_filter, grism) if 'Open' not in name][0]
    return Band.lookup(filter_name)


