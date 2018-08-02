import subprocess as sp
import glob 

import astropy
from astropy.nddata import CCDData
import astropy.io.fits as fits


files = [i for i in glob.glob('*.fits') if not 'check' in i and not 'sexout' in i and not 'astroreffed' in i]

for file in files:
    prefix = file.split('.')[0]
    checkfile = prefix+'_check.fits'
    catfile = prefix+'_sexout.fits'
    headerfile = catfile.replace('.fits', '.head')
    astroreffed = prefix+'_astroreffed.fits'

    sp.run(['sex', '-c', 'sex.config', file,
            '-CHECKIMAGE_TYPE', 'OBJECTS', '-CHECKIMAGE_NAME', checkfile,
            '-CATALOG_NAME', catfile])

    # print(['ds9', '-tile', checkfile, '-histequ', file, '-log'])
    sp.Popen(['ds9', '-tile', checkfile, '-histequ', file, '-log'], shell=False,
             stdin=sp.PIPE, stdout=sp.PIPE, stderr=sp.PIPE, close_fds=True)

    sp.run(['scamp', catfile, '-c', 'scamp.config'])

    scamp_data = open(headerfile, 'r').read()

    image_data = CCDData.read(file)
    scamp_header = fits.Header.fromstring(scamp_data, sep='\n')

    for entry in scamp_header.copy():
        # PV?_? entries are not handled well by wcslib and by extension astropy
        if entry.startswith('PV'):
            scamp_header.pop(entry)

    print("original wcs:\n", image_data.wcs)
    print("updated wcs:\n", astropy.wcs.WCS(scamp_header))

    # So you could use update(**header). That would interpret the header as a dictionary, which does not work for
    # comment and History, as they can be present multiple times
    image_data.header.update(scamp_header)
    image_data.wcs = astropy.wcs.WCS(scamp_header)

    image_data.write(astroreffed, overwrite=True)

