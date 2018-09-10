from ldac import *
%pylab
# run sextractor, scamp
# Need MAG_BEST, MAGERR_BEST in sex.config and SAVE_REFCATALOG in scamp.config

# read scamp output catalog, header -> wcs and sextractor output cat

scamp_header = fits.Header.fromtextfile('sexout.head')
wcs=astropy.wcs.WCS(scamp_header)
gaia=get_table_from_ldac('GAIA-DR1_1915+0719_r4.cat')
sex = get_table_from_ldac('sexout.fits')
# hacky way to go over pandas -> else we get a structured array that world2pix cannot handle
# origin does not seem to really matter...
gaia_px=wcs.all_world2pix(np.array(gaia['X_WORLD','Y_WORLD'].to_pandas()),1)
sex_world=wcs.wcs_pix2world(np.array(sex['XWIN_IMAGE','YWIN_IMAGE'].to_pandas()),1)

plt.scatter(gaia['X_WORLD'], gaia['Y_WORLD'])
plt.scatter(sex_world[:, 0], sex_world[:, 1])
