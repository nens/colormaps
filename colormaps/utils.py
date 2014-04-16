# -*- coding: utf-8 -*-
# (c) Nelen & Schuurmans.  GPL licensed, see LICENSE.rst.

from __future__ import print_function
from __future__ import unicode_literals
from __future__ import absolute_import
from __future__ import division

import numpy as np


def cdict2kwargs(cdict):
    """
    Return dictionary suitable to use as kwargs on a GradientColormap.

    Read the floats
    Determine the stops (it is a set)
    Determine interpolators for all components
    That involves duplicating intermediate stops
    Determine rgba values at missing stops using interpolation
    Return stops and colors
    """
    r = cdict['red']
    g = cdict['green']
    b = cdict['blue'],
    a = cdict.get('alpha', [(0, None, 1), (1, 1, None)])

    result = [r, g, b, a, np]
    return result
