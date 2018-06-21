
#TODO CCDData.read might crash due to WCS.to_header() in some astropy installations
images =  [astropy.nddata.CCDData.read(image) for image in image_paths]
flats = [astropy.nddata.CCDData.read(image) for image in flat_paths]
bads = [astropy.nddata.CCDData.read(image) for image in bad_paths]


for path in image_paths:
    with fits.open(path) as stack:
        print(len(stack))
        for ext in stack[1:]:
            print(ext.header['Date-obs'],ext.header['exptime'])

files = ccdproc.ImageFileCollection('.', keywords='*')

filter_vals = ('H', 'J', 'Ks')
filter_column = 'NCFLTNM2'

for filter_val in filter_vals:
    images = files.hdus(**{filter_column:filter_val})


images = [ccdproc.flat_correct(img, flats[0]) for img in images]
