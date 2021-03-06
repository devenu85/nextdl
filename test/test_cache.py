#!/usr/bin/env python
# coding: utf-8

from __future__ import unicode_literals

# Allow direct execution
import os
import shutil
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


from test.helper import Fakendl

from nextdl.cache import Cache


def _is_empty(d):
    return not bool(os.listdir(d))


def _mkdir(d):
    if not os.path.exists(d):
        os.mkdir(d)


class TestCache(unittest.TestCase):
    def setUp(self):
        TEST_DIR = os.path.dirname(os.path.abspath(__file__))
        TESTDATA_DIR = os.path.join(TEST_DIR, "testdata")
        _mkdir(TESTDATA_DIR)
        self.test_dir = os.path.join(TESTDATA_DIR, "cache_test")
        self.tearDown()

    def tearDown(self):
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_cache(self):
        ndl = Fakendl(
            {
                "cachedir": self.test_dir,
            }
        )
        c = Cache(ndl)
        obj = {"x": 1, "y": ["ä", "\\a", True]}
        self.assertEqual(c.load("test_cache", "k."), None)
        c.store("test_cache", "k.", obj)
        self.assertEqual(c.load("test_cache", "k2"), None)
        self.assertFalse(_is_empty(self.test_dir))
        self.assertEqual(c.load("test_cache", "k."), obj)
        self.assertEqual(c.load("test_cache", "y"), None)
        self.assertEqual(c.load("test_cache2", "k."), None)
        c.remove()
        self.assertFalse(os.path.exists(self.test_dir))
        self.assertEqual(c.load("test_cache", "k."), None)


if __name__ == "__main__":
    unittest.main()
