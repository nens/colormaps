# -*- coding: utf-8 -*-
# (c) Nelen & Schuurmans.  GPL licensed, see LICENSE.rst.

from __future__ import print_function
from __future__ import unicode_literals
from __future__ import absolute_import
from __future__ import division

import json
import os

from colormaps import core

PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), 'data'))


class Manager(object):
    """ Loads colormaps from a path. """
    sep = ':'

    def get_key(self, path):
        relpath = os.path.relpath(path, self.path)
        return os.path.splitext(relpath)[0].replace(os.path.sep, self.sep)

    def get_id(self, path):
        return os.path.splitext(os.path.basename(path))[0]

    def __init__(self, path=PATH):
        self.path = path

        # read data
        self.inventory = []
        for basedir, dirnames, filenames in os.walk(path):
            for filename in filenames:
                self.inventory.append(os.path.join(basedir, filename))

        # build dict
        self.registered = {self.get_id(p): p for p in self.inventory}

    @property
    def keys(self):
        return sorted([(self.get_key(p),
                        self.get_id(p)) for p in self.inventory])

    def get(self, name):
        if name in core.registered:
            return core.registered[name]
        if name in self.registered:
            colormap = core.create(json.load(open(self.registered[name])))
            colormap.register(name)
            return colormap
        raise NameError("'{}' is not in registered colormaps".format(name))
