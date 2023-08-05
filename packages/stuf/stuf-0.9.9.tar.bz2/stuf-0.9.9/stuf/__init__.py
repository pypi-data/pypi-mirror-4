# -*- coding: utf-8 -*-
'''dictionaries with attribute-style access.'''

from stuf.iterable import (
    exhaustmap as exhaustitems, exhaustcall as exhaustmap, exhauststar)
from stuf.core import defaultstuf, fixedstuf, frozenstuf, orderedstuf, stuf

__version__ = (0, 9, 9)
__all__ = 'defaultstuf fixedstuf frozenstuf orderedstuf stuf'.split()
