import astropy.io.fits
import astropy.table
import astropy.wcs
import matplotlib.pyplot as plt
import numpy as np
from astropy.nddata import CCDData


def transient_detection(sextractor_output: str, refcat: str, reffed_image: CCDData):
    image = CCDData.read(reffed_image)
    wcs = image.wcs

    gaia = astropy.table.Table(
        astropy.io.fits.open(refcat)[2].data)  # third hdu, get the numpy recarray, convert to astropy table
    sex = astropy.table.Table(astropy.io.fits.open(sextractor_output)[2].data)

    # origin does not seem to really matter...
    gaia_px = wcs.all_world2pix(np.array(gaia['X_WORLD', 'Y_WORLD'].to_pandas()), 1)
    gaia['X_IMAGE'] = gaia_px[:, 0]
    gaia['Y_IMAGE'] = gaia_px[:, 1]
    sex_world = wcs.wcs_pix2world(np.array(sex['XWIN_IMAGE', 'YWIN_IMAGE'].to_pandas()), 1)

    # Do calculations in image coordinates so we can use error to estimate same-ness of detections

    distinct = []
    ambig = []
    notfound = []
    min_starclassifier = 0.8

    for row in sex[sex['CLASS_STAR'] > 0.8]:
        x, y = row['XWIN_IMAGE'], row['YWIN_IMAGE']
        xerr, yerr = row['ERRX2WIN_IMAGE'], row['ERRY2WIN_IMAGE']

        xcol, ycol = gaia_px[:, 0], gaia_px[:, 1]

        # how far out of the sextractor reported measurement error for the centroid do we want to search
        scale = 100
        candidate_idx = (xcol > x - xerr * scale) * (xcol < x + xerr * scale) * (ycol > y - yerr * scale) * (
                    ycol < y + yerr * scale)
        n_candidates = sum(candidate_idx)

        if n_candidates == 1:
            # check here for brightness difference. Problem right now is that magnitudes have very different offsets
            distinct.append((row, gaia[candidate_idx]))

        if n_candidates == 0:
            # we found a new star????
            notfound.append(row)

        else:
            ambig.append((row, gaia[candidate_idx]))

    print('N ClassStar>',min_starclassifier, ':', len(sex[sex['CLASS_STAR'] > 0.8]))
    print('distinct: ', len(distinct))
    print('notfound: ', len(notfound))
    print('ambiguous: ', len(ambig))

    plt.scatter(gaia_px[:, 0], gaia_px[:, 1], marker='o', color='g',label='reference stars')
    plt.scatter(sex['XWIN_IMAGE'],sex['YWIN_IMAGE'], color='r', marker='x', label='sextractor')
    plt.legend()

    # plt.figure()
    # plt.scatter([d[0]['XWIN_IMAGE'] for d in distinct], [d[0]['YWIN_IMAGE'] for d in distinct], color='red')
    # plt.scatter([d[1]['X_IMAGE'] for d in distinct], [d[1]['Y_IMAGE'] for d in distinct], color='green')

    # plt.scatter([d['XWIN_IMAGE'] for d in notfound], [d['YWIN_IMAGE'] for d in notfound], color='pink')

    # plt.scatter(gaia['X_WORLD'], gaia['Y_WORLD'])
    # plt.scatter(sex_world[:, 0], sex_world[:, 1])




    plt.show()
    return sex, gaia
