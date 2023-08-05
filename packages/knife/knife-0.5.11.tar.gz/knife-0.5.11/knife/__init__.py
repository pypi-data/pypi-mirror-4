# -*- coding: utf-8 -*-
'''Things go in. Things happen. Things come out.'''

from knife.lazy import lazyknife
from knife.active import activeknife

knife = activeknife
__ = lazyknife

__all__ = ('knife', 'activeknife', 'lazyknife', '__')

__version__ = (0, 5, 11)
