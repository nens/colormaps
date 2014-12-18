# -*- coding: utf-8 -*-
# (c) Nelen & Schuurmans.  GPL licensed, see LICENSE.rst.

from __future__ import print_function
from __future__ import unicode_literals
from __future__ import absolute_import
from __future__ import division

import os
import shutil
import tempfile
import unittest

import numpy as np

import colormaps
from colormaps import core
from colormaps import utils

MASKED = [0, 0, 255, 255]
INVALID = [0, 255, 0, 255]


def discrete():
    colormap = {
        'type': 'DiscreteColormap',
        'masked': MASKED,
        'invalid': INVALID,
        'data': [
            (0, (127, 000, 000, 255)),
            (2, (255, 000, 000, 255)),
        ],
        'labels': {'en_EN': {0: 'label0', 2: 'label2'}}
    }
    return colormaps.create(colormap)


def gradient(size=3, log=False, free=True, interp=None):
    colormap = {
        'type': 'GradientColormap',
        'size': size,
        'free': free,
        'log': log,
        'interp': interp,
        'masked': MASKED,
        'data': [
            (3, (127, 000, 000, 255)),
            (5, (255, 000, 000, 255)),
        ],
    }
    return colormaps.create(colormap)


def cdict():
    return {
        'blue': (
            (0.000, 0.5, 0.5),
            (0.110, 1.0, 1.0),
            (0.340, 1.0, 1.0),
            (0.650, 0.0, 0.0),
            (1.000, 0.0, 0.0)
        ),
        'green': (
            (0.000, 0.0, 0.0),
            (0.125, 0.0, 0.0),
            (0.375, 1.0, 1.0),
            (0.640, 1.0, 1.0),
            (0.910, 0.0, 0.0),
            (1.000, 0.0, 0.0)
        ),
        'red': (
            (0.000, 0.0, 0.0),
            (0.350, 0.0, 0.0),
            (0.660, 1.0, 1.0),
            (0.890, 1.0, 1.0),
            (1.000, 0.5, 0.5)
        )
    }


class TestColormap(unittest.TestCase):
    def test_gradient_repr(self):
        colormap = gradient()
        self.assertTrue(repr(colormap))

    def test_gradient_size(self):
        colormap = gradient(size=5)
        self.assertEqual(len(colormap), 5)

    def test_gradient_clip(self):
        colormap = gradient()
        self.assertEqual(
            colormap(7, limits=(7, 9)).tolist(),
            [127, 000, 000, 255],
        )

    def test_gradient_interp(self):
        colormap = gradient(log=True, interp=[(3, 0), (5, 1)])
        self.assertEqual(
            colormap(7).tolist(),
            [255, 000, 000, 255],
        )

    def test_gradient_interp_and_clip(self):
        colormap = gradient(interp=[(3, 0), (5, 1)])
        self.assertEqual(
            colormap(7, limits=(4, 6)).tolist(),
            [255, 000, 000, 255],
        )

    def test_gradient_non_free(self):
        colormap = gradient(free=False)
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

    def test_gradient_no_labels(self):
        colormap = gradient()
        self.assertEqual(colormap.label([5, 6]), [5, 6])

    def test_discrete_repr(self):
        colormap = discrete()
        self.assertTrue(repr(colormap))

    def test_discrete_clip(self):
        colormap = discrete()
        self.assertEqual(
            colormap(0, limits=(1, 2)).tolist(),
            MASKED,
        )

    def test_discrete_label(self):
        colormap = discrete()
        self.assertEqual(colormap.label(0), 'label0')
        self.assertEquals(colormap.label([0, 1, 2]), ['label0', 1, 'label2'])

    def test_discrete(self):
        colormap = discrete()
        # scalar
        self.assertEqual(colormap(np.ma.masked).tolist(), MASKED)
        self.assertEqual(colormap(5).tolist(), MASKED)
        self.assertEqual(colormap(2).tolist(), [255, 000, 000, 255])
        # array
        self.assertEqual(
            colormap(np.ma.masked_equal([0, 1, 2, 3], 2)).tolist(),
            [[127, 000, 000, 255],
             INVALID,
             MASKED,
             MASKED],
        )

    def test_data_repr(self):
        data = core.Data(data=(2, 3), limits=(1, 4))
        self.assertEqual(repr(data), '<Data: data 2,3; limits 1,4>')

    def test_register(self):
        name = 'test'
        colormap = discrete()
        colormap.register(name)
        self.assertEqual(colormap, colormaps.get(name))

    def test_not_registered(self):
        self.assertRaises(NameError, colormaps.get, 'nonsense')


class TestManager(unittest.TestCase):
    def test_manager(self):
        manager = colormaps.Manager()
        # check for duplicate keys
        self.assertEqual(len(manager.keys), len(manager.registered))
        # load from disk
        colormap = manager.get('landuse')  # load path
        self.assertIsInstance(colormap, core.DiscreteColormap)
        # return from cache
        colormap = manager.get('landuse')  # cache path
        self.assertIsInstance(colormap, core.DiscreteColormap)
        # labeling with existing labels
        self.assertEquals(colormap.label([1]),
                          ['1 - BAG - Overig / Onbekend'])
        # not existing colormap
        self.assertRaises(NameError, manager.get, 'blabla')
        # not existing colormap, not existing labels
        colormap = manager.get('jet')
        self.assertEqual(colormap.label([5, 6]), [5, 6])


class TestUtils(unittest.TestCase):
    def test_cdict2config(self):
        config = {
            'type': u'GradientColormap',
            'data': [(0.000,   [0,   0, 127, 255]),
                     (0.110,    [0,  0, 255, 255]),
                     (0.125,   [0,   0, 255, 255]),
                     (0.340,   [0, 219, 255, 255]),
                     (0.350,   [0, 229, 246, 255]),
                     (0.375,  [20, 255, 226, 255]),
                     (0.640, [238, 255,   8, 255]),
                     (0.650, [246, 245,   0, 255]),
                     (0.660, [255, 236,   0, 255]),
                     (0.890, [255,  18,   0, 255]),
                     (0.910, [231, 000,   0, 255]),
                     (1.000, [127, 000,   0, 255])],
            }
        self.assertEqual(utils.cdict2config(cdict()), config)

    def test_save(self):
        name = 'test'
        path = tempfile.mkdtemp()
        here = os.getcwd()
        os.chdir(path)
        utils.save(cdict=cdict(), name=name)
        os.chdir(here)
        self.assertTrue(
            os.path.exists(os.path.join(path, '{}.json'.format(name))),
        )
        shutil.rmtree(path)
