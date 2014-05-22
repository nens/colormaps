# -*- coding: utf-8 -*-
# (c) Nelen & Schuurmans.  GPL licensed, see LICENSE.rst.

from __future__ import print_function
from __future__ import unicode_literals
from __future__ import absolute_import
from __future__ import division

import numpy as np

EPS = {
    np.dtype('f2'): np.finfo(np.dtype('f2')).eps,
    np.dtype('f4'): np.finfo(np.dtype('f4')).eps,
    np.dtype('f8'): np.finfo(np.dtype('f8')).eps,
}

registered_colormaps = {}


class BaseColormap(object):
    def register(self, name):
        """ Register a colormap for use with get(). """
        registered_colormaps[name] = self


class GradientColormap(BaseColormap):

    def __init__(self, stops, colors, n=1024):
        """
        - determine scale offset where stops go from 0.5 to n + 0.5
        """
        self.rgba = np.empty((n, 4), 'u1')

        a, b = min(stops), max(stops)
        values = np.arange(n) / (n - 1) * (b - a) + a
        for i, c in enumerate(zip(*colors)):
            self.rgba[:, i] = np.interp(values, stops, c)

        self.limits = a, b

    def __call__(self, data):
        d = np.array(data, 'f8')
        n = len(self.rgba)
        e = EPS[d.dtype]
        a, b = self.limits
        rgba = self.rgba[np.uint64(n * ((d - (a + e)) / (b - a)))]
        return rgba


class DiscreteColormap(BaseColormap):

    def __init__(self, values, colors):
        self.rgba = np.zeros((max(values) + 1, 4), dtype='u1')
        self.rgba[np.array(values)] = colors

    def __call__(self, data):
        d = np.array(data, 'i8')
        rgba = self.rgba[d]
        return rgba


def get(name):
    return registered_colormaps.get(name)
