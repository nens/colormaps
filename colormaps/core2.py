
# -*- coding: utf-8 -*-
# (c) Nelen & Schuurmans.  GPL licensed, see LICENSE.rst.

from __future__ import print_function
from __future__ import unicode_literals
from __future__ import absolute_import
from __future__ import division

import collections
import numpy as np
import sys

EPS = np.finfo(np.dtype('f8')).eps

registered = {}


class Data(object):
    """ 
    Convenience wrapper for data.

    scale() will typically be called with the colormaps' limits as the
    clip limits.
    """
    def __init__(self, data, limits=None):
        self.array = np.ma.array(data)
        if limits is None:
            self.limits = np.array([self.array.min(), self.array.max()])
        else:
            self.limits = limits
    
    def clip(self, vmin=-np.inf, vmax=np.inf):
        return self.__class__(data=self.data.clip(vmin, vmax),
                              limits=self.limits.clip(vmin, vmax))

    def log(self):
        return self.__class__(data=np.ma.log(data), limits=np.ma.log(limits))

    def scale(self, vmin=None, vmax=None, log=False):
        # clip when necessary
        if vmin is not None or vmax is not None:
            data = self.clip(vmin, vmax)
        else:
            data = self

        factor = data.limits[1] - data.limits[0]
        offset = data.limits[0]

        if log:
            factor *= np.e - 1
            offset -= 1
        scaled = self.__class__(
            data=(self.data - offset) * factor,
            limits=(self.limits - offset) * factor,
        )

        return scaled.log() if log else scaled


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

    def __init__(self, values, colors, segments=256, scale='linear'):
        """
        Instantiate scale.


        """
        a, b = min(values), max(values)
        if scale == 'logarithmic':
            pass
            # first scale to between 1 and e, then log.
        elif scale == 'linear':
            # scale to between 0 and 1
            scale = Linear
        else:
            scale = Interpolation(x, y)
    
        self.rgba = np.empty((n, 4), 'u1')

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
