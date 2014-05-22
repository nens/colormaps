# -*- coding: utf-8 -*-
# (c) Nelen & Schuurmans.  GPL licensed, see LICENSE.rst.

from __future__ import print_function
from __future__ import unicode_literals
from __future__ import absolute_import
from __future__ import division

import unittest

import numpy as np

import colormaps


def discrete():
    data = np.empty((256, 256), 'u1')
    for i in range(8):
        data[32 * i:32 * (i + 1)] = i

    values, colors = zip(*[
        (0, (255, 000, 000, 255)),
        (1, (255, 255, 000, 255)),
        (2, (000, 255, 000, 255)),
        (3, (000, 255, 255, 255)),
        (4, (000, 000, 255, 255)),
        (5, (255, 000, 000, 127)),
        (6, (000, 255, 000, 127)),
        (7, (000, 000, 255, 127)),
    ])
    colormap = colormaps.DiscreteColormap(values=values, colors=colors)
    return data, colormap


def gradient():
    data = np.empty((256, 256))
    data[:] = np.arange(256) / 255
    stops, colors = zip(*[
        (0.2, (255, 000, 000, 255)),
        (0.5, (000, 255, 000, 255)),
        (1.3, (000, 000, 255, 255)),
    ])
    colormap = colormaps.GradientColormap(stops=stops, colors=colors)
    return data, colormap


class TestColormap(unittest.TestCase):
    def test_gradient(self):
        data, colormap = gradient()
        rgba = colormap(data)
        rgba
        self.assertEqual(colormap(0.2).tolist(), [255, 000, 000, 255])
        self.assertEqual(colormap(0.5).tolist(), [000, 255, 000, 255])
        self.assertEqual(colormap(0.9).tolist(), [000, 127, 127, 255])
        self.assertEqual(colormap(1.3).tolist(), [000, 000, 255, 255])

    def test_discrete(self):
        data, colormap = discrete()
        rgba = colormap(data)
        rgba
        self.assertEqual(colormap(0).tolist(), [255, 0, 0, 255])

    def test_register(self):
        name = 'test'
        data, colormap = discrete()
        colormap.register(name)
        self.assertEqual(colormap, colormaps.get(name))
