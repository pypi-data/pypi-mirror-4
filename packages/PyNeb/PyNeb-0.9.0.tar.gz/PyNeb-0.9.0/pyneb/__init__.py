"""
PyNeb - python package for the analysis of emission lines
"""

__all__ = []
__version__ = '0.9.0'

import sys
from numpy.version import version as numpy_version


class VersionError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

if sys.version_info[0:2] < (2, 6):
    raise VersionError('Python version >= 2.6 needed')
 
try:
    if [int(n) for n in (numpy_version.split('.')[:3])] < [1, 5, 1] :
        raise VersionError('Numpy version >= 1.5.1 needed')
except:
    raise VersionError('I do not understand what is your version of numpy, report this to PyNeb group')
try:
    import pyfits
except:
    raise ImportError('PyFITS package needed')

from utils.Config import _Config
config = _Config()
log_ = config.log_
log_.message('Starting PyNeb version %s' %__version__, calling = 'PyNeb')

from utils.manage_atomic_data import _ManageAtomicData
atomicData = _ManageAtomicData()

atomicData.defaultDict = 'PYNEB_13_01'
atomicData.resetDataFileDict()

from utils.fits import Hdr, writeAtom, writeColl

from core.pynebcore import Atom, RecAtom, getAtomDict, getRecEmissivity, EmissionLine, Observation, \
    parseLineLabel
from core.icf import ICF 
from core.diags import Diagnostics, diags_dict
from core.emisGrid import EmisGrid, getEmisGridDict
from plot.plotAtomicData import DataPlot
from utils.physics import CST
from utils.saverestore import save, restore
from utils.init import LINE_LABEL_LIST, BLEND_LIST
from extinction.red_corr import RedCorr

log_.message('PyNeb ready.', calling = 'PyNeb')
log_.timer('Starting PyNeb version %s' %__version__, quiet = True, calling = 'PyNeb')
