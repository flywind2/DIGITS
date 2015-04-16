# Copyright (c) 2014-2015, NVIDIA CORPORATION.  All rights reserved.

import os.path
import tempfile
import shutil
from cStringIO import StringIO

from nose.tools import raises, assert_raises
import mock
import unittest
import PIL.Image
import numpy as np

from . import create_db as _

class TestInit():
    @classmethod
    def setUpClass(cls):
        cls.db_name = tempfile.mkdtemp()

    @classmethod
    def tearDownClass(cls):
        try:
            shutil.rmtree(cls.db_name)
        except OSError:
            pass

    @raises(ValueError)
    def test_bad_backend(self):
        """invalid db backend"""
        _.DbCreator(self.db_name, 'not-a-backend')

class TestPathToDatum():
    @classmethod
    def setUpClass(cls):
        cls.tmpdir = tempfile.mkdtemp()
        cls.db_name = tempfile.mkdtemp(dir=cls.tmpdir)
        cls.db = _.DbCreator(cls.db_name, 'lmdb')
        _handle, cls.image_path = tempfile.mkstemp(dir=cls.tmpdir, suffix='.jpg')
        with open(cls.image_path, 'w') as outfile:
            PIL.Image.fromarray(np.zeros((10,10,3),dtype=np.uint8)).save(outfile, format='JPEG', quality=100)

    @classmethod
    def tearDownClass(cls):
        try:
            shutil.rmtree(cls.tmpdir)
        except OSError:
            pass

    def test_configs(self):
        """path_to_datum"""
        self.db.height = 10
        self.db.width = 10
        self.db.resize_mode = 'squash'
        self.db.image_folder = None
        for e in ['none', 'png', 'jpg']:
            for c in [1, 3]:
                for m in [True, False]:
                    yield self.check_configs, (e, c, m)

    def check_configs(self, args):
        e, c, m = args
        self.db.encoding = e
        self.db.channels = c
        self.db.compute_mean = m
        image_sum = self.db.initial_image_sum()
        d = self.db.path_to_datum(self.image_path, 0, image_sum)
        assert (d.channels, d.height, d.width) == (self.db.channels, self.db.height, self.db.width), 'wrong datum shape'
        if e == 'none':
            assert not d.encoded, 'datum should not be encoded when encoding="%s"' % e
        else:
            assert d.encoded, 'datum should be encoded when encoding="%s"' % e

class TestSaveMean():
    pass
