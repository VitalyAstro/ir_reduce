from enum import Enum, auto


class Category(Enum):
    IMAGING = auto()
    SPECTROSCOPY = auto()
    BAD = auto()
    FLAT = auto()
    BIAS = auto()
    TECHNICAL = auto()
    UNKNOWN = auto()


class Band(Enum):

    @classmethod
    def lookup(cls, value):
        """Reverse of the []-operator to access by value->name, not name->value"""
        for entry in cls:
            if entry.value == value:
                return entry

    # Notcam
    H = 'H'
    J = 'J'
    Ks = 'Ks'

    # ALF
    ubes = 'U_Bes 362_60'
    bbes = 'B_Bes 440_100'
    iint = 'i_int 797_157'
    rbes = 'R_Bes 650_130'
    vbes = 'V_Bes 530_80'

    gsdss = "g'_SDSS 480_145"
    isdss = "i'_SDSS 771_171"
    rsdss = "r'_SDSS  618_148"
    zsdss = "z'_SDSS  832_LP"
    usdss = "u'_SDSS  353_55"

    grism = 'Grism_#4'


class Instrument(Enum):
    NOTCAM = auto()
    ALFOSC = auto()
    UNKNOWN = auto()
