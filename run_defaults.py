import ir_reduce
if __name__ == '__main__':
    import glob
    ir_reduce.do_everything(['./testdata/bad_zero_sci.fits'], ['./testdata/FlatJ.fits'], glob.glob('./testdata/NCAc0708*.fits'),
                  output='pythonout.fits')