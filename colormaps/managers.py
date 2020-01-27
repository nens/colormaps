# -*- coding: utf-8 -*-
# (c) Nelen & Schuurmans, see LICENSE.rst.

import json
import os

from colormaps import core

BASE_PATH = os.path.dirname(__file__)
DATA_PATH = os.path.abspath(os.path.join(BASE_PATH, 'data'))
LABELS_PATH = os.path.abspath(os.path.join(BASE_PATH, 'labels'))


class Manager(object):
    """ Loads colormaps from a path. """
    sep = ':'

    def get_key(self, path):
        relpath = os.path.relpath(path, self.path)
        return os.path.splitext(relpath)[0].replace(os.path.sep, self.sep)

    def get_id(self, path):
        return os.path.splitext(os.path.basename(path))[0]

    def load_label(self, path):
        with open(path) as json_file:
            return dict(json.load(json_file))

    def get_labels(self, name):
        """ Return locale dict of label dicts. """
        base = os.path.join(LABELS_PATH, name)
        if not os.path.exists(base):
            return {}
        names = os.listdir(base)
        paths = [os.path.join(base, n) for n in names]
        locales = [os.path.splitext(n)[0] for n in names]
        return {l: self.load_label(p) for l, p in zip(locales, paths)}

    def __init__(self, path=DATA_PATH):
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
            with open(self.registered[name]) as f:
                config = json.load(f)
            config['labels'] = self.get_labels(name)
            colormap = core.create(config)
            colormap.register(name)
            return colormap
        raise NameError("'{}' is not in registered colormaps".format(name))
