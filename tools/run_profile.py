import ir_reduce
import cProfile, pstats
from pstats import SortKey
from pyprof2calltree import convert


pr = cProfile.Profile()
pr.enable()
ir_reduce.do_everything(['../testdata/bad_cold5.fits', '../testdata/bad_hot2.fits', '../testdata/bad_zero_sci.fits'],
    ['../testdata/FlatJ.fits'],
    ["../testdata/NCAc070865.fits", "../testdata/NCAc070866.fits", "../testdata/NCAc070867.fits",
     "../testdata/NCAc070868.fits",
     "../testdata/NCAc070869.fits",
     "../testdata/NCAc070870.fits",
     "../testdata/NCAc070871.fits",
     "../testdata/NCAc070872.fits",
     "../testdata/NCAc070873.fits",
     "../testdata/NCAc070874.fits",
     "../testdata/NCAc070875.fits",
     "../testdata/NCAc070876.fits",
     "../testdata/NCAc070877.fits",
     "../testdata/NCAc070878.fits", "../testdata/NCAc070879.fits", "../testdata/NCAc070880.fits",
     "../testdata/NCAc070881.fits", "../testdata/NCAc070882.fits", "../testdata/NCAc070883.fits", "../testdata/NCAc070884.fits",
     "../testdata/NCAc070885.fits", "../testdata/NCAc070886.fits", "../testdata/NCAc070887.fits", "../testdata/NCAc070888.fits",
     "../testdata/NCAc070889.fits", "../testdata/NCAc070890.fits",
     "../testdata/NCAc070891.fits"],
                        output=False)

pr.disable()
pr.dump_stats('multicore.stats')
convert(pr.getstats(), 'multicore.kgrind')

prsingle = cProfile.Profile()
ir_reduce.Pool = ir_reduce.PoolDummy

prsingle.enable()
ir_reduce.do_everything(['../testdata/bad_cold5.fits', '../testdata/bad_hot2.fits', '../testdata/bad_zero_sci.fits'],
    ['../testdata/FlatJ.fits'],
    ["../testdata/NCAc070865.fits", "../testdata/NCAc070866.fits", "../testdata/NCAc070867.fits",
     "../testdata/NCAc070868.fits",
     "../testdata/NCAc070869.fits",
     "../testdata/NCAc070870.fits",
     "../testdata/NCAc070871.fits",
     "../testdata/NCAc070872.fits",
     "../testdata/NCAc070873.fits",
     "../testdata/NCAc070874.fits",
     "../testdata/NCAc070875.fits",
     "../testdata/NCAc070876.fits",
     "../testdata/NCAc070877.fits",
     "../testdata/NCAc070878.fits", "../testdata/NCAc070879.fits", "../testdata/NCAc070880.fits",
     "../testdata/NCAc070881.fits", "../testdata/NCAc070882.fits", "../testdata/NCAc070883.fits", "../testdata/NCAc070884.fits",
     "../testdata/NCAc070885.fits", "../testdata/NCAc070886.fits", "../testdata/NCAc070887.fits", "../testdata/NCAc070888.fits",
     "../testdata/NCAc070889.fits", "../testdata/NCAc070890.fits",
     "../testdata/NCAc070891.fits"],
                        output=False)
prsingle.disable()
prsingle.dump_stats('singlecore.stats')
convert(prsingle.getstats(), 'singlecore.kgrind')

print("\n\n\n\n_______ multithreaded _______ \n\n\n\n")
ps = pstats.Stats(pr).sort_stats(SortKey.CUMULATIVE)
ps.print_stats('.*ir_reduce.*')

ps = pstats.Stats(pr).sort_stats(SortKey.TIME)
ps.print_stats('.*ir_reduce.*')

print("\n\n\n\n_______ singlethread _______ \n\n\n\n")
ps = pstats.Stats(prsingle).sort_stats(SortKey.CUMULATIVE)
ps.print_stats('.*ir_reduce.*')

ps = pstats.Stats(prsingle).sort_stats(SortKey.TIME)
ps.print_stats('.*ir_reduce.*')