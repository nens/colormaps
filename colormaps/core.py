# -*- coding: utf-8 -*-
# (c) Nelen & Schuurmans, see LICENSE.rst.

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
    def __repr__(self):
        template = '<{name}: data {dmin},{dmax}; limits {lmin},{lmax}>'
        return template.format(lmin=self.limits[0],
                               lmax=self.limits[1],
                               dmin=self.data.min(),
                               dmax=self.data.max(),
                               name=self.__class__.__name__)

    def __init__(self, data, limits=None):
        """
        If limits, clip data right from start.

        :param data: a numpy data
        :param limits: min, max tuple
        """
        if limits is None:
            self.data = np.asarray(data)  # does not copy if data is array
            self.limits = np.array([self.data.min(), self.data.max()])
        else:
            if limits[1] < limits[0]:
                limits = limits[::-1]
            self.limits = np.array(limits)
            self.data = np.asarray(data).clip(*self.limits)

    def do(self, function):
        """ Apply func to both array and limits. """
        return self.__class__(data=function(self.data),
                              limits=function(self.limits))

    def log(self):
        """ Transform to log domain. """
        return self.do(lambda x: np.log(x))

    def interp(self, interp):
        """ Interpolate. """
        return self.do(lambda x: np.interp(x, *interp))

    def scale(self):
        """ Scale limits and data to span (0, 1). """
        factor = self.limits[1] - self.limits[0]
        if factor == 0:
            # single value, return 0.5
            return self.do(lambda x: np.full(x.shape, 0.5, dtype='f8'))
        offset = self.limits[0]

        # scale
        return self.do(lambda x: (x - offset) / factor)


class BaseColormap(object):
    """ Basic stuff """
    colormap_type = 'base'

    def register(self, name):
        """ Register a colormap for use with get(). """
        registered[name] = self

    def label(self, data, locale=None):
        """ Return a list of labels. """
        if not self.labels:
            return data
        labels = self.labels.get(locale, next(iter(self.labels.values())))
        return np.vectorize(
            lambda x: labels.get(x, x), otypes=[np.object],
        )(data).tolist()

    def __len__(self):
        """
        Return the official length of the rgba array.

        The actual rgba is one element bigger, for different reasons. The
        DiscreteColormap uses it for storing the 'masked' color. The
        GradientColormap uses it so that the highest value, that is 1.0
        after scaling, does not fall out of the rgba array when looking
        up by index.
        """
        return len(self.rgba) - 1

    def __call__(self, data, limits=None):
        """
        Return rgba array, handle masked values.

        :param data: dict('values': np.array, 'no_data_value': number)
        :param limits: m, n tuple having m <= n.

        The effect of the limits parameter dependes on the colormap type
        """
        if isinstance(data, dict):
            values = np.asarray(data['values'])
            mask = np.equal(values, data['no_data_value'])
        elif isinstance(data, np.ma.MaskedArray):
            values = data.data
            mask = data.mask
        else:
            values = np.asarray(data)
            mask = None

        # also mask non-finite values (-inf, inf, nan)
        nan_mask = ~np.isfinite(values)
        mask = nan_mask if mask is None else mask | nan_mask

        if not np.any(mask):  # np.any(None) returns False
            return self.convert(values, limits)
        rgba = self.masked * np.ones(values.shape + (4,), 'u1')
        if not mask.all():
            rgba[~mask] = self.convert(values[~mask], limits)
        return rgba


class DiscreteColormap(BaseColormap):
    """ Colormap for classified data. """
    colormap_type = 'discrete'

    def __repr__(self):
        template = '<{name}: size {size}, limits {lower}-{upper}>'
        return template.format(size=len(self),
                               lower=self.limits[0],
                               upper=self.limits[1],
                               name=self.__class__.__name__)

    def __init__(self, data, masked=MASKED, invalid=INVALID, labels={}):
        """
        Build the look-up table.
        """
        values, colors = zip(*data)

        self.limits = min(values), max(values)
        self.masked = np.array(masked, 'u1')
        self.invalid = np.array(invalid, 'u1')
        self.labels = {k: dict(v) for k, v in labels.items()}
        self.rgba = self.invalid * np.ones((self.limits[1] + 2, 4), dtype='u1')
        self.rgba[-1] = self.masked
        self.rgba[np.array(values)] = colors

    def convert(self, data, limits):
        """"
        Return rgba.

        :param data: A numpy array, not masked.
        :param limits: m, n tuple having m <= n.

        Values outside the limits will be colored with the masked color,
        even if a value was given during the colormap initialization.
        """
        # tighten limits to colormap
        if limits is None:
            limits = self.limits
        else:
            limits = np.array(limits).clip(*self.limits)

        # mask data outside limits
        index = data.astype(np.int64)
        out_of_bounds = (index < limits[0]) | (index > limits[1])
        if index.ndim == 0:  # these cannot be indexed
            if out_of_bounds:
                index = self.limits[1] + 1
        else:
            index[out_of_bounds] = self.limits[1] + 1
        return self.rgba[index]

    def get_legend_data(self, limits, steps):
        """For a discrete map, we ignore 'steps'."""
        if limits is None:
            limits = self.limits
        else:
            # tighten custom limits to colormap
            limits = np.array(limits).clip(*self.limits)

        return np.in1d(
            self.rgba.view('u4')[limits[0]:limits[1] + 1],
            self.invalid.view('u4'), invert=True,
        ).nonzero()[0] + limits[0]


class GradientColormap(BaseColormap):
    colormap_type = 'gradient'

    def __repr__(self):
        template = ('<{name}: size {size}, '
                    'limits {lower} - {upper}, log {log}, interp {interp}>')
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

        Returned data is clipped between 0 and 1.
        """
        data = Data(data=data, limits=limits)
        if self.interp:
            data = data.interp(self.interp)
        if self.log:
            data = data.log()
        data = data.scale()

        # return the clipped array
        return data.data.clip(0, 1)

    def __init__(self, data,
                 size=256, log=False, free=True,
                 interp=None, masked=MASKED, labels={}):
        """
        Build the look-up table.

        :param data: list of (number, rgba tuple) that defines the stops
        :param size: size of the generated look-up table
        :param free: use data limits instead of colormap limits
        :param log: use a log scale whenever appropriate
        :param interp: [(x1, y1), (x2, y2), ...]
        :param masked: rgba tuple to use as masked color
        """
        values, colors = zip(*data)

        # options
        self.log = log
        self.free = free
        self.masked = np.array(masked, 'u1')
        self.labels = {k: dict(v) for k, v in labels.items()}
        self.limits = min(values), max(values)

        # store interpolation inputs
        if interp is not None:
            xp, yp = list(np.array(interp, dtype='f8').transpose())
            # np.interp assumes sorted x values
            sort_inds = np.argsort(xp)
            self.interp = xp[sort_inds], yp[sort_inds]
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

        # data is between 0 and 1, and self.rgba deliberately has a repeated
        # last element to handle data elements that have the value 1
        return self.rgba[np.int64(len(self) * data)]

    def get_legend_data(self, limits, steps):
        """We need to interpolate the range, then take a linear range between
        those interpolated values, then extrapolate the range back.

        If this is a log colormap, first log the range, then exp the results
        back."""
        if limits is None:
            limits = self.limits

        if self.log:
            limits = np.log(limits)

        if self.interp:
            interpolated = np.interp(limits, self.interp[0], self.interp[1])
            linear = np.linspace(interpolated[0], interpolated[1], steps)
            data = np.interp(linear, self.interp[1], self.interp[0])
        else:
            data = np.linspace(limits[0], limits[1], steps)

        if self.log:
            data = np.exp(data)

        return data


def get(name):
    try:
        return registered[name]
    except KeyError:
        raise NameError("'{}' is not in registered colormaps".format(name))


def create(colormap):
    """ Create a colormap from a dictionary. """
    kwargs = colormap.copy()
    return getattr(sys.modules[__name__], kwargs.pop('type'))(**kwargs)
