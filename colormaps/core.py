
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
        if data is None:
            self.array, self.limits = array, limits
        else:
            self.array = np.array(data)
            self.limits = np.array([self.array.min(), self.array.max()])

    def do(self, function):
        """ Apply func to both array and limits. """
        return self.__class__(array=function(self.array),
                              limits=function(self.limits))

    def clip(self, limits):
        """ Clip between vmin and vmax. """
        return self.do(lambda x: x.clip(*limits))

    def log(self):
        """ Transform to log domain. """
        return self.do(lambda x: np.log(x * (np.e - 1) + 1))

    def interp(self, x, y):
        """ Interpolate. """
        return self.do(lambda z: np.interp(z, x, y))

    def scale(self, limits):
        """ Linear normalize, using limits or data limits. """
        if limits is None:
            # use own limits
            data = self
        else:
            # clip to given limits
            data = self.clip(limits)
        factor = data.limits[1] - data.limits[0]
        if factor == 0:
            # single value, return 0.5
            return self.do(lambda x: 0.5 * np.ones(x.shape, x.dtype))

        # scale
        offset = data.limits[0]
        return data.do(lambda x: (x - offset) / factor)


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
        :param limits: m, n tuple having m <= n.

        Values outside the limits will be colored with the invalid color,
        even if a value was given during the colormap initialization.
        """
        if limits is None:
            limits = self.limits
        else:
            limits = np.array(limits).clip(self.limits)
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
        data = Data(data)
        if limits is None:
            if self.interp is not None:
                # use linear interpolation into the (0, 1) range
                return data.interp(self.interp)
        if self.log:
            # use linear scaling into the (0, 1) range followed by log rescale
            return data.scale(limits).log()
        # use linear scaling into the (0, 1) range
        return data.scale(limits)

    def __init__(self, values, colors,
                 size=256, log=False, free=True, interp=None, masked=None):
        """
        Build the look-up table.

        :param values: list of N floats
        :param colors: list of N rgba tuples
        :param size: size of the generated look-up table
        :param log: use a log scale whenever appropriate
        :param free: use data limits instead of colormap limits
        :param interp: {'sources': sources, 'targets': targets}
        :param masked: rgba tuple to use as masked color
        """
        if interp:
            self.interp = (np.array(interp['sources']),
                           np.array(interp['targets']))
        else:
            self.interp = None
        self.log = log
        self.free = free
        self.masked = masked
        self.limits = min(values), max(values)

        stops = self.process(data=values).array
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
        return self.rgba[np.uint64(len(self) * data.array)]


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
