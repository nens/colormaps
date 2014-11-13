# -*- coding: utf-8 -*-
# (c) Nelen & Schuurmans.  GPL licensed, see LICENSE.rst.

from __future__ import print_function
from __future__ import unicode_literals
from __future__ import absolute_import
from __future__ import division

import collections
import json
import numpy as np
import sys

EPS = np.finfo(np.dtype('f8')).eps

registered = {}


class BaseColormap(object):
    def register(self, name):
        """ Register a colormap for use with get(). """
        registered[name] = self

    def __call__(self, data):
        """ Return rgba array. """
        if np.ma.isMaskedArray(data):
            s = data.shape
            m = data.mask
            if m.any():
                rgba = np.zeros(s + (4,), 'u1')
                if not m.all():
                    d = data.compressed().astype(self.dtype)
                    rgba[~m] = self.convert(d)
                return rgba
            # masked array, but nothing masked
        d = np.array(data, self.dtype)
        return self.convert(d)


class GradientColormap(BaseColormap):
    dtype = np.dtype('f8')

    def __init__(self, stops, colors, n=1024):
        """
        Determine scale and offset that place the stops at (0.5) and
        (n + 0.5). Or not? Also create a look-up table for scaled data.
        """
        self.rgba = np.empty((n, 4), 'u1')

        a, b = min(stops), max(stops)
        values = np.arange(n) / (n - 1) * (b - a) + a
        for i, c in enumerate(zip(*colors)):
            self.rgba[:, i] = np.interp(values, stops, c)

        self.limits = a, b

    def convert(self, data):
        """
        Return rgba.

        :param data: A numpy array, not masked.
        """
        n = len(self.rgba)
        a, b = self.limits
        return self.rgba[np.uint64(n * ((data - (a + EPS)) / (b - a)))]


class DiscreteColormap(BaseColormap):
    dtype = np.dtype('u8')

    def __init__(self, values, colors):
        self.rgba = np.zeros((max(values) + 1, 4), dtype='u1')
        self.rgba[np.array(values)] = colors

    def convert(self, data):
        """"
        Return rgba.

        :param data: A numpy array, not masked.
        """
        return self.rgba[data]


def normalize(data, vmin=None, vmax=None):
    if not np.ma.isMaskedArray(data):
        data = np.array(data)
    dmin = data.min() if vmin is None else vmin
    dmax = data.max() if vmax is None else vmax
    return (data - dmin) / (dmax - dmin)


def get(name):
    try:
        return registered[name]
    except KeyError:
        raise NameError("'{}' is not in registered colormaps".format(name))


def load(path):
    with open(path) as f:
        d = json.load(f)
        args = collections.defaultdict(list, **d['args'])
        for c in d['components']:
            for k, v in c.items():
                args['{}s'.format(k)].append(v)
        return getattr(sys.modules[__name__], d['type'])(**args)
