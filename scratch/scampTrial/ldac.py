# Copyright 2015 Fred Moolekamp
# BSD 3-clause license
"""
Functions to convert FITS files or astropy Tables to FITS_LDAC files and
vice versa.
"""

def convert_hdu_to_ldac(hdu):
    """
    Convert an hdu table to a fits_ldac table (format used by astromatic suite)
    
    Parameters
    ----------
    hdu: `astropy.io.fits.BinTableHDU` or `astropy.io.fits.TableHDU`
        HDUList to convert to fits_ldac HDUList
    
    Returns
    -------
    tbl1: `astropy.io.fits.BinTableHDU`
        Header info for fits table (LDAC_IMHEAD)
    tbl2: `astropy.io.fits.BinTableHDU`
        Data table (LDAC_OBJECTS)
    """
    from astropy.io import fits
    import numpy as np
    tblhdr = np.array([hdu.header.tostring(',')])
    col1 = fits.Column(name='Field Header Card', array=tblhdr, format='13200A')
    cols = fits.ColDefs([col1])
    tbl1 = fits.BinTableHDU.from_columns(cols)
    tbl1.header['TDIM1'] = '(80, {0})'.format(len(hdu.header))
    tbl1.header['EXTNAME'] = 'LDAC_IMHEAD'
    tbl2 = fits.BinTableHDU(hdu.data)
    tbl2.header['EXTNAME'] = 'LDAC_OBJECTS'
    return (tbl1, tbl2)

def convert_table_to_ldac(tbl):
    """
    Convert an astropy table to a fits_ldac
    
    Parameters
    ----------
    tbl: `astropy.table.Table`
        Table to convert to ldac format
    Returns
    -------
    hdulist: `astropy.io.fits.HDUList`
        FITS_LDAC hdulist that can be read by astromatic software
    """
    from astropy.io import fits
    import tempfile
    f = tempfile.NamedTemporaryFile(suffix='.fits', mode='rb+')
    tbl.write(f.name, format='fits',overwrite='true')
    f.seek(0)
    hdulist = fits.open(f.name, mode='update')
    tbl1, tbl2 = convert_hdu_to_ldac(hdulist[1])
    new_hdulist = [hdulist[0], tbl1, tbl2]
    new_hdulist = fits.HDUList(new_hdulist)
    return new_hdulist

def save_table_as_ldac(tbl, filename, **kwargs):
    """
    Save a table as a fits LDAC file
    
    Parameters
    ----------
    tbl: `astropy.table.Table`
        Table to save
    filename: str
        Filename to save table
    kwargs:
        Keyword arguments to pass to hdulist.writeto
    """
    hdulist = convert_table_to_ldac(tbl)
    hdulist.writeto(filename, **kwargs)

def get_table_from_ldac(filename, frame=1):
    """
    Load an astropy table from a fits_ldac by frame (Since the ldac format has column 
    info for odd tables, giving it twce as many tables as a regular fits BinTableHDU,
    match the frame of a table to its corresponding frame in the ldac file).
    
    Parameters
    ----------
    filename: str
        Name of the file to open
    frame: int
        Number of the frame in a regular fits file
    """
    from astropy.table import Table
    if frame>0:
        frame = frame*2
    tbl = Table.read(filename, hdu=frame)
    return tbl

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

