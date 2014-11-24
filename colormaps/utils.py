# -*- coding: utf-8 -*-
# (c) Nelen & Schuurmans.  GPL licensed, see LICENSE.rst.

from __future__ import print_function
from __future__ import unicode_literals
from __future__ import absolute_import
from __future__ import division

import numpy as np


def cdict2config(cdict):
    """
    Return dictionary suitable to use as kwargs on a GradientColormap.

    Read the floats
    Determine the stops (it is a set)
    Determine interpolators for all components
    That involves duplicating intermediate stops
    Determine rgba values at missing stops using interpolation
    Return stops and colors
    """
    # stops
    values = sorted(set(d[0] for v in cdict.values() for d in v))

    # interpolators per color
    interps = {}
    for color, data in cdict.items():
        x = []
        y = []
        for i in range(len(data) - 1):
            a = data[i]
            b = data[i + 1]
            x.extend([a[0], b[0]])
            y.extend([a[2], b[1]])
        interps[color] = np.array(x), np.array(y)

    # create data
    index = {'red': 0, 'green': 1, 'blue': 2, 'alpha': 3}
    floats = np.ones((len(values), 4))
    for color, interp in interps.items():
        floats[:, index[color]] = np.interp(values, *interp)
        integers = (255 * floats).astype('u1')
    return {'type': 'GradientColormap',
            'data': zip(values, integers.tolist())}


def save(cdict, name):
    """ Save a raster-server specific colormap file. """
    data = cdict2config(cdict)['data']
    template = '      [{v:.3f}, [{r:3}, {g:3}, {b:3}, {a}]]{c}\n'

    with open('{name}.json'.format(name=name), 'w') as target:
        target.write('{\n  "type": "GradientColormap",\n  "data": [\n')
        for v, (r, g, b, a) in data[:-1]:
            target.write(template.format(v=v, r=r, g=g, b=b, a=a, c=','))
        v, (r, g, b, a) = data[-1]
        target.write(template.format(v=v, r=r, g=g, b=b, a=a, c=''))
        target.write('  ]\n}')
