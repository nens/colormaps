# -*- coding: utf-8 -*-
# (c) Nelen & Schuurmans.  GPL licensed, see LICENSE.rst.

from __future__ import print_function
from __future__ import unicode_literals
from __future__ import absolute_import
from __future__ import division

import numpy as np
import sys

MASKED = 0, 0, 0, 0
INVALID = 0, 0, 0, 0

registered = {}


class Data(object):
    """
    Convenience wrapper for data.

    scale() will typically be called with the colormaps' limits as the
    clip limits.
    """
    def __init__(self, data, limits=None):
        """
        If limits, clip data right from start.

        :param data: a numpy data
        :param limits: min, max tuple
        """
        if limits is None:
            self.data = np.array(data)
            self.limits = np.array([self.data.min(), self.data.max()])
        else:
            self.limits = np.array(limits)
            self.data = np.array(data).clip(*self.limits)

    def do(self, function):
        """ Apply func to both array and limits. """
        return self.__class__(data=function(self.data),
                              limits=function(self.limits))

    def log(self):
        """ Transiform to log domain. """
        return self.do(lambda x: np.log(x))

    def interp(self, interp):
        """ Interpolate. """
        return self.do(lambda x: np.interp(x, *interp))

    def scale(self):
        """ Scale limits and data to span (0, 1). """
        factor = self.limits[1] - self.limits[0]
        if factor == 0:
            # single value, return 0.5
            return self.do(lambda x: 0.5 * np.ones(x.shape, x.dtype))
        offset = self.limits[0]

        # scale
        return self.do(lambda x: (x - offset) / factor)


class BaseColormap(object):
    """ Basic stuff """
    def register(self, name):
        """ Register a colormap for use with get(). """
        registered[name] = self

    def __len__(self):
        """
        Return the official length of the rgba array.

        The actual rgba is one element bigger, for different reasons. The
        DiscreteColormap uses it for storing the invalid color. The
        GradientColormap uses it so that the highest value, that is 1.0
        after scaling, does not fall out of the rgba array when looking
        up by index.
        """
        return len(self.rgba) - 1

    def __call__(self, data, limits=None):
        """
        Return rgba array, handle masked values.

        :param data: the data to colormap
        :param limits: m, n tuple having m <= n.

        The effect of the limits parameter dependes on the colormap type
        """
        array = np.ma.array(data)
        mask = array.mask
        if not mask.any():
            return self.convert(array.data, limits)
        rgba = self.masked * np.ones(array.shape + (4,), 'u1')
        if not mask.all():
            rgba[~mask] = self.convert(array.compressed(), limits)
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

    def __init__(self, values, colors, masked=MASKED, invalid=INVALID):
        """
        Build the look-up table.
        """
        self.limits = min(values), max(values)
        self.rgba = invalid * np.ones((self.limits[1] + 2, 4), dtype='u1')
        self.rgba[np.array(values)] = colors
        self.masked = np.array(masked, 'u1')

    def convert(self, data, limits):
        """"
        Return rgba.

        :param data: A numpy array, not masked.
        :param limits: m, n tuple having m <= n.

        Values outside the limits will be colored with the invalid color,
        even if a value was given during the colormap initialization.
        """
        # tighten limits to colormap
        if limits is None:
            limits = self.limits
        else:
            limits = np.array(limits).clip(self.limits)
        
        # mask data outside limits
        index = np.ma.masked_outside(
            np.uint64(data), limits[0], limits[1],
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

        If limits are not given, data is scaled according to the colormaps
        interpolation, if any, or else to the input limits.
        """
        data = Data(data=data, limits=limits)
        if self.log:
            data = data.log()
        if self.interp:
            data = data.interp(self.interp)
            if limits:
                data = data.scale()
        else:
            data = data.scale()
        return data.data

    def __init__(self, values, colors,
                 size=256, free=True, log=False, interp=None, masked=INVALID):
        """
        Build the look-up table.

        :param values: list of N floats
        :param colors: list of N rgba tuples
        :param size: size of the generated look-up table
        :param free: use data limits instead of colormap limits
        :param log: use a log scale whenever appropriate
        :param interp: [(x1, y1), (x2, y2), ...]
        :param masked: rgba tuple to use as masked color
        """
        self.log = log
        self.free = free
        self.masked = np.array(masked, 'u1')
        self.limits = min(values), max(values)

        # store interpolation inputs scaled
        if interp:
            self.interp = map(np.array, zip(*interp))
            if log:
                np.log(self.interp[0], self.interp[0])
        else:
            self.interp = None

        # now the color entries
        stops = self.process(data=values)
        values = np.arange(size) / (size - 1)

        # build the color table
        self.rgba = np.empty((size + 1, 4), 'u1')
        for i, c in enumerate(zip(*colors)):
            self.rgba[: -1, i] = np.interp(values, stops, c)
        self.rgba[-1, :] = self.rgba[-2, :]

    def convert(self, data, limits):
        """
        Return rgba.

        :param data: A numpy array, not masked.
        :param limits: m, n tuple having m <= n.

        If limits are given, input is scaled such that values between
        limits span the colormap. Values outside are colored according
        to the first and last entries in the colormap.

        If limits are not given, limits are taken from input if the
        colormap is 'free' or else from the colormap initialization
        values.
        """
        if limits is None and not self.free:
            limits = self.limits

        data = self.process(data=data, limits=limits)
        return self.rgba[np.uint64(len(self) * data)]


def get(name):
    try:
        return registered[name]
    except KeyError:
        raise NameError("'{}' is not in registered colormaps".format(name))


def create(colormap):
    """ Create a colormap from a dictionary. """
    kwargs = colormap.copy()
    values, colors = zip(*kwargs.pop('data'))
    kwargs.update(values=values, colors=colors)
    return getattr(sys.modules[__name__], kwargs.pop('type'))(**kwargs)
