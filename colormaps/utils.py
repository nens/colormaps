# -*- coding: utf-8 -*-
# (c) Nelen & Schuurmans.  GPL licensed, see LICENSE.rst.

from __future__ import print_function
from __future__ import unicode_literals
from __future__ import absolute_import
from __future__ import division

def cdict2kwargs(cdict):
    """
    Convert cdict and retun a dictionary.
    
    Convert the matplotlib cdict to kwargs suitable for the instantiation
    of a GradientColormap.
    How:
    - Make a set of stops from all components
    - Need the final array as soon asap
    - 
    - Duplicate stops if direction matters
    - Interpolate the missing values.
    - 
    """
    for c in ['red', 'green', 'blue', 'alpha']:
        cdict.get(c)
