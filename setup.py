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
from __future__ import print_function

import os.path
import sys
import warnings

try:
    from setuptools import Command, setup

    setuptools_available = True
except ImportError:
    from distutils.core import Command, setup

    setuptools_available = False
from distutils.spawn import spawn

try:
    # This will create an exe that needs Microsoft Visual C++ 2008
    # Redistributable Package
    import py2exe
except ImportError:
    if len(sys.argv) >= 2 and sys.argv[1] == "py2exe":
        print("Cannot import py2exe", file=sys.stderr)
        exit(1)

py2exe_options = {
    "bundle_files": 1,
    "compressed": 1,
    "optimize": 2,
    "dist_dir": ".",
    "dll_excludes": ["w9xpopen.exe", "crypt32.dll"],
}

# Get the version from nextdl/version.py without importing the package
exec(compile(open("nextdl/version.py").read(), "nextdl/version.py", "exec"))

DESCRIPTION = "YouTube video downloader"
LONG_DESCRIPTION = (
    "Command-line program to download videos from YouTube.com and other video sites"
)

py2exe_console = [
    {
        "script": "./nextdl/__main__.py",
        "dest_base": "nextdl",
        "version": __version__,
        "description": DESCRIPTION,
        "comments": LONG_DESCRIPTION,
        "product_name": "nextdl",
        "product_version": __version__,
    }
]

py2exe_params = {
    "console": py2exe_console,
    "options": {"py2exe": py2exe_options},
    "zipfile": None,
}

if len(sys.argv) >= 2 and sys.argv[1] == "py2exe":
    params = py2exe_params
else:
    files_spec = [
        ("etc/bash_completion.d", ["nextdl.bash-completion"]),
        ("etc/fish/completions", ["nextdl.fish"]),
        ("share/doc/nextdl", ["README.txt"]),
        ("share/man/man1", ["nextdl.1"]),
    ]
    root = os.path.dirname(os.path.abspath(__file__))
    data_files = []
    for dirname, files in files_spec:
        resfiles = []
        for fn in files:
            if not os.path.exists(fn):
                warnings.warn(
                    "Skipping file %s since it is not present. Type  make  to build all automatically generated files."
                    % fn
                )
            else:
                resfiles.append(fn)
        data_files.append((dirname, resfiles))

    params = {
        "data_files": data_files,
    }
    if setuptools_available:
        params["entry_points"] = {"console_scripts": ["nextdl = nextdl:main"]}
    else:
        params["scripts"] = ["bin/nextdl"]


class build_lazy_extractors(Command):
    description = "Build the extractor lazy loading module"
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        spawn(
            [
                sys.executable,
                "devscripts/make_lazy_extractors.py",
                "nextdl/extractor/lazy_extractors.py",
            ],
            dry_run=self.dry_run,
        )


setup(
    name="nextdl",
    version=__version__,
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    url="https://github.com/nextdl/nextdl",
    author="nextdl",
    author_email="nextdl@nextdl.org",
    license="MIT",
    packages=[
        "nextdl",
        "nextdl.extractor",
        "nextdl.downloader",
        "nextdl.postprocessor",
    ],
    # Provokes warning on most systems (why?!)
    # test_suite = 'nose.collector',
    # test_requires = ['nosetest'],
    classifiers=[
        "Topic :: Multimedia :: Video",
        "Development Status :: 5 - Production/Stable",
        "Environment :: Console",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.2",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: Implementation",
        "Programming Language :: Python :: Implementation :: CPython",
    ],
    cmdclass={"build_lazy_extractors": build_lazy_extractors},
    **params
)
