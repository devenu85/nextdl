"""
MIT License

Copyright (c) 2021 nextdl

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
from __future__ import unicode_literals

import errno
import io
import json
import os
import re
import shutil
import traceback

from .compat import compat_getenv
from .utils import expand_path, write_json_file


class Cache(object):
    def __init__(self, ndl):
        self._ndl = ndl

    def _get_root_dir(self):
        res = self._ndl.params.get("cachedir")
        if res is None:
            cache_root = compat_getenv("XDG_CACHE_HOME", "~/.cache")
            res = os.path.join(cache_root, "nextdl")
        return expand_path(res)

    def _get_cache_fn(self, section, key, dtype):
        assert re.match(r"^[a-zA-Z0-9_.-]+$", section), "invalid section %r" % section
        assert re.match(r"^[a-zA-Z0-9_.-]+$", key), "invalid key %r" % key
        return os.path.join(self._get_root_dir(), section, "%s.%s" % (key, dtype))

    @property
    def enabled(self):
        return self._ndl.params.get("cachedir") is not False

    def store(self, section, key, data, dtype="json"):
        assert dtype in ("json",)

        if not self.enabled:
            return

        fn = self._get_cache_fn(section, key, dtype)
        try:
            try:
                os.makedirs(os.path.dirname(fn))
            except OSError as ose:
                if ose.errno != errno.EEXIST:
                    raise
            write_json_file(data, fn)
        except Exception:
            tb = traceback.format_exc()
            self._ndl.report_warning("Writing cache to %r failed: %s" % (fn, tb))

    def load(self, section, key, dtype="json", default=None):
        assert dtype in ("json",)

        if not self.enabled:
            return default

        cache_fn = self._get_cache_fn(section, key, dtype)
        try:
            try:
                with io.open(cache_fn, "r", encoding="utf-8") as cachef:
                    return json.load(cachef)
            except ValueError:
                try:
                    file_size = os.path.getsize(cache_fn)
                except (OSError, IOError) as oe:
                    file_size = str(oe)
                self._ndl.report_warning(
                    "Cache retrieval from %s failed (%s)" % (cache_fn, file_size)
                )
        except IOError:
            pass  # No cache available

        return default

    def remove(self):
        if not self.enabled:
            self._ndl.to_screen(
                "Cache is disabled (Did you combine --no-cache-dir and --rm-cache-dir?)"
            )
            return

        cachedir = self._get_root_dir()
        if not any((term in cachedir) for term in ("cache", "tmp")):
            raise Exception(
                "Not removing directory %s - this does not look like a cache dir"
                % cachedir
            )

        self._ndl.to_screen("Removing cache dir %s ." % cachedir, skip_eol=True)
        if os.path.exists(cachedir):
            self._ndl.to_screen(".", skip_eol=True)
            shutil.rmtree(cachedir)
        self._ndl.to_screen(".")
