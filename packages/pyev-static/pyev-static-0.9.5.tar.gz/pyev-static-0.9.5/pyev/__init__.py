"""Python bindings to libev."""
from __future__ import absolute_import

VERSION = (0, 9, 5)

__version__ = '.'.join(map(str, VERSION[0:3]))
__author__ = 'Malek Hadj-Ali'
__contact__ = 'lekmalek@gmail.com'
__homepage__ = 'http://packages.python.org/pyev/'
__docformat__ = 'restructuredtext'

# -eof meta-


#-----------------------------------------------------------------------------
# Imports
#-----------------------------------------------------------------------------

import os
import sys
import glob

# load bundled libev, if there is one:

here = os.path.dirname(__file__)

bundled = []
for ext in ('pyd', 'so', 'dll', 'dylib'):
    bundled.extend(glob.glob(os.path.join(here, 'libev*.%s*' % ext)))

if bundled:
    import ctypes
    if bundled[0].endswith('.pyd'):
        # a Windows Extension
        _libev = ctypes.cdll.LoadLibrary(bundled[0])
    else:
        _libev = ctypes.CDLL(bundled[0], mode=ctypes.RTLD_GLOBAL)
    del ctypes

del os, sys, glob, here, bundled, ext


# pyev top-level imports
from pyev._pyev import *


# specify module interface
import os
from pyev import _pyev

__all__ = []
__all__.extend(os._get_exports_list(_pyev))
