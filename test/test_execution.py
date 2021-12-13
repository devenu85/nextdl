#!/usr/bin/env python
# coding: utf-8

from __future__ import unicode_literals

import os
import subprocess
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from nextdl.utils import encodeArgument

rootDir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


try:
    _DEV_NULL = subprocess.DEVNULL
except AttributeError:
    _DEV_NULL = open(os.devnull, "wb")


class TestExecution(unittest.TestCase):
    def test_import(self):
        subprocess.check_call([sys.executable, "-c", "import nextdl"], cwd=rootDir)

    def test_module_exec(self):
        if sys.version_info >= (2, 7):  # Python 2.6 doesn't support package execution
            subprocess.check_call(
                [sys.executable, "-m", "nextdl", "--version"],
                cwd=rootDir,
                stdout=_DEV_NULL,
            )

    def test_main_exec(self):
        subprocess.check_call(
            [sys.executable, "nextdl/__main__.py", "--version"],
            cwd=rootDir,
            stdout=_DEV_NULL,
        )

    def test_cmdline_umlauts(self):
        p = subprocess.Popen(
            [sys.executable, "nextdl/__main__.py", encodeArgument("ä"), "--version"],
            cwd=rootDir,
            stdout=_DEV_NULL,
            stderr=subprocess.PIPE,
        )
        _, stderr = p.communicate()
        self.assertFalse(stderr)

    def test_lazy_extractors(self):
        try:
            subprocess.check_call(
                [
                    sys.executable,
                    "devscripts/make_lazy_extractors.py",
                    "nextdl/extractor/lazy_extractors.py",
                ],
                cwd=rootDir,
                stdout=_DEV_NULL,
            )
            subprocess.check_call(
                [sys.executable, "test/test_all_urls.py"], cwd=rootDir, stdout=_DEV_NULL
            )
        finally:
            try:
                os.remove("nextdl/extractor/lazy_extractors.py")
            except (IOError, OSError):
                pass


if __name__ == "__main__":
    unittest.main()
