
# -*- coding: utf-8 -*-
# (c) Nelen & Schuurmans.  GPL licensed, see LICENSE.rst.

from __future__ import print_function
from __future__ import unicode_literals
from __future__ import absolute_import
from __future__ import division

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
    def __init__(self, data=None, limits=None, array=None):
        """ Either supply data, or array and limits. """
        if data:
            self.array = np.array(data)
            self.limits = np.array([self.array.min(), self.array.max()])
        else:
            self.array, self.limits = array, limits

    def do(self, function):
        """ Apply func to both array and limits. """
        return self.__class__(array=function(self.array),
                              limits=function(self.limits))

    def clip(self, domain):
        """ Clip between vmin and vmax. """
        return self.do(lambda x: x.clip(*domain))

    def log(self):
        """ Transform to log domain. """
        return self.do(lambda x: np.log(x * (np.e - 1) + 1))
    
    def interp(self, x, y):
        """ Interpolate. """
        return self.do(lambda z: np.interp(z, x, y))

    def scale(self, limits):
        """ Linear normalize, using domain or self.limits. """
        data = self.clip(limits)
        factor = limits[1] - limits[0]
        offset = limits[0]
        return data.do(lambda x: (x - offset) / factor)


class BaseColormap(object):
    """ Basic stuff """
    def register(self, name):
        """ Register a colormap for use with get(). """
        registered[name] = self

    def __len__(self):
        return len(self.rgba)

    def __call__(self, data, limits=None):
        """ Return rgba array, handle masked arrays. """
        a = np.ma.array(data)
        m = a.mask
        if not m.any():
            return self.convert(a.data, limits)
        rgba = self.masked * np.ones(a.shape + (4,), 'u1')
        if not m.all():
            rgba[~m] = self.convert(a.compressed(), limits)
        return rgba


class DiscreteColormap(BaseColormap):
    """ Colormap for classified data. """
    dtype = np.dtype('u8')

    def __repr__(self):
        template = '<{name}: size {size}, limits {lower}-{upper}>'
        return template.format(size=len(self),
                               lower=self.limits[0],
                               upper=self.limits[1],
                               name=self.__class__.__name__)

    def __init__(self, values, colors, masked=None, invalid=None):
        """
        Build the look-up table.
        """
        self.limits = min(values), max(values)
        self.rgba = invalid * np.ones((self.limits[1] + 2, 4), dtype='u1')
        self.rgba[np.array(values)] = colors
        self.masked = masked

    def convert(self, data, limits):
        """"
        Return rgba.

        :param data: A numpy array, not masked.
        """
        index = np.ma.masked_outside(
            np.uint64(data), self.limits[0], self.limits[1],
        ).filled(self.limits[1] + 1)
        return self.rgba[index]


class GradientColormap(BaseColormap):
    dtype = np.dtype('f8')

    def __repr__(self):
        template = ('<{name}: size {size}, '
                    'limits {lower}-{upper}, log {log}, interp {interp}>')
        return template.format(log=self.log,
                               size=len(self),
                               lower=self.limits[0],
                               upper=self.limits[1],
                               interp=self.interp is not None,
                               name=self.__class__.__name__)

    def process(self, data, limits=None):
        """
        Return processed data.

        Process data according to colormap properties and domain request.
        """
        data = Data(data)
        if limits is None:
            if self.interp is not None:
                # use linear interpolation into the (0, 1) range
                return data.interp(self.interp)
            if self.limits is not None:
                limits = self.limits
        if self.log:
            # use linear scaling into the (0, 1) range followed by log rescale
            return data.scale(limits).log()
        # use linear scaling into the (0, 1) range
        return data.scale(limits)

    def __init__(self, values, colors,
                 size=256, log=False, interp=None, masked=None):
        """
        Build the look-up table.
        """
        if interp:
            self.interp = (np.array(interp['sources']),
                           np.array(interp['targets']))
        else:
            self.interp = None
        self.log = log
        self.masked = masked
        self.limits = min(values), max(values)

        stops = self.process(data=values).array
        values = np.arange(size) / (size - 1)

        # build the color table
        self.rgba = np.empty((size, 4), 'u1')
        for i, c in enumerate(zip(*colors)):
            self.rgba[:, i] = np.interp(values, stops, c)

    def convert(self, data, limits):
        """
        Return rgba.

        :param data: A numpy array, not masked.
        """
        data = self.process(data=data, limits=limits)
        (a, b) = self.limits if limits is None else data.limits
        n = len(self)
        return self.rgba[np.uint64(n * ((data.array - (a + EPS)) / (b - a)))]


def get(name):
    try:
        return registered[name]
    except KeyError:
        raise NameError("'{}' is not in registered colormaps".format(name))


def create(colormap):
    """ Create a colormap from a dictionary. """
    kwargs = colormap.copy()

    # rearrange the items
    kwargs.update(values=[], colors=[])
    for element in kwargs.pop('items'):
        for k, v in element.items():
            kwargs['{}s'.format(k)].append(v)

    # rearrange interp
    interp = kwargs.pop('interp', None)
    if interp:
        kwargs['interp'] = {'sources': [], 'targets': []}
        for element in interp:
            for k, v in element.items():
                kwargs['interp']['{}s'.format(k)].append(v)

    return getattr(sys.modules[__name__], kwargs.pop('type'))(**kwargs)
