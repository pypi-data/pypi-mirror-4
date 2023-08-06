"""
pyUnihan

Lookup for unihan

Copyright (c) 2013, Louie Lu.
License: MIT (see LICENSE for details)
"""

__author__ = 'Louie Lu'
__version__ = '0.0.1'
__license__ = 'MIT'

import sys

py = sys.version_info
py3k = py >= (3, 0, 0)

if py3k:
    from pyunihan import *
else:
    from pyunihan import *

init()