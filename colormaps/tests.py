# -*- coding: utf-8 -*-
# (c) Nelen & Schuurmans.  GPL licensed, see LICENSE.rst.

from __future__ import print_function
from __future__ import unicode_literals
from __future__ import absolute_import
from __future__ import division

import unittest

import numpy as np

import colormaps

MASKED = [0, 0, 255, 255]
INVALID = [0, 255, 0, 255]


def discrete():
    colormap = {
        'type': 'DiscreteColormap',
        'masked': MASKED,
        'invalid': INVALID,
        'items': [
            {'value': 0, 'color': (127, 000, 000, 255)},
            {'value': 2, 'color': (255, 000, 000, 255)},
        ],
    }
    return colormaps.create(colormap)


def gradient(size=3, log=False, free=True, interp=None):
    colormap = {
        'type': 'GradientColormap',
        'masked': MASKED,
        'items': [
            {'value': 3, 'color': (127, 000, 000, 255)},
            {'value': 5, 'color': (255, 000, 000, 255)},
        ],
        'log': log,
        'free': free,
        'interp': interp,
    }
    return colormaps.create(colormap)


class TestColormap(unittest.TestCase):
    def test_gradient_repr(self):
        colormap = gradient()
        self.assertTrue(repr(colormap))
    
    def test_gradient_clip(self):
        colormap = gradient()
        self.assertEqual(
            colormap(7, limits=(7, 9)).tolist(),
            [127, 000, 000, 255],
        )
    
    def test_gradient_non_free(self):
        colormap = gradient(free=False)
        self.assertEqual(
            colormap(7).tolist(),
            [255, 000, 000, 255],
        )

    def test_gradient_interp(self):
        colormap = gradient(log=True, interp=[
            {'source': 3, 'target': 0},
            {'source': 5, 'target': 1},
        ])
        self.assertEqual(
            colormap(7).tolist(),
            [255, 000, 000, 255],
        )

    def test_gradient_log(self):
        colormap = gradient(log=True)
        self.assertEqual(
            colormap(7, limits=(7, 9)).tolist(),
            [127, 000, 000, 255],
        )

    def test_gradient(self):
        colormap = gradient()
        # scalars
        m = np.ma.masked
        self.assertEqual(colormap(m).tolist(), MASKED)
        self.assertEqual(colormap(7).tolist(), [191, 000, 000, 255])
        # array
        self.assertEqual(
            colormap(np.ma.masked_equal([2, 3, 4, 6], 3)).tolist(),
            [[127, 000, 000, 255],
             MASKED,
             [191, 000, 000, 255],
             [255, 000, 000, 255]]
        )

    def test_discrete_repr(self):
        colormap = discrete()
        self.assertTrue(repr(colormap))
    
    def test_discrete_clip(self):
        colormap = discrete()
        self.assertEqual(
            colormap(0, limits=(1, 2)).tolist(),
            INVALID,
        )
    
    def test_discrete(self):
        colormap = discrete()
        # scalar
        self.assertEqual(colormap(np.ma.masked).tolist(), MASKED)
        self.assertEqual(colormap(5).tolist(), INVALID)
        self.assertEqual(colormap(2).tolist(), [255, 000, 000, 255])
        # array
        self.assertEqual(
            colormap(np.ma.masked_equal([0, 1, 2, 3], 1)).tolist(),
            [[127, 000, 000, 255],
             MASKED,
             [255, 000, 000, 255],
             INVALID],
        )

    def test_register(self):
        name = 'test'
        colormap = discrete()
        colormap.register(name)
        self.assertEqual(colormap, colormaps.get(name))

    def test_not_registered(self):
        self.assertRaises(NameError, colormaps.get, 'nonsense')
