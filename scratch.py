
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


def standard_process_old():
    processed = dict()
    for idx, filter_val in enumerate(filter_vals):
        images_with_filter = [image for image in images if image.header[filter_column] == filter_val]
        flat = flats[idx]

        reduceds = []
        for image in images_with_filter:
            image.mask = bad
            # TODO that's from the quicklook-package, probably would want to do this individually for every sensor area
            gain = (image.header['GAIN1'] + image.header['GAIN2'] + image.header['GAIN3'] + image.header['GAIN4']) / 4
            readnoise = (image.header['RDNOISE1'] + image.header['RDNOISE2'] + image.header['RDNOISE3'] + image.header[
                'RDNOISE4']) / 4
            reduced = ccdproc.ccd_process(image,
                                          oscan=None,
                                          error=True,
                                          gain=gain * u.electron / u.count,
                                          # TODO check if this is right or counts->adu required
                                          readnoise=readnoise * u.electron,
                                          dark_frame=None,
                                          master_flat=flat,
                                          bad_pixel_mask=bad)
            reduceds.append(reduced)
        processed[filter_val] = reduceds
    return processed