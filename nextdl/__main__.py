#!/usr/bin/env python
from __future__ import unicode_literals

import sys

# Execute with
# $ python nextdl/__main__.py (2.6+)
# $ python -m nextdl          (2.7+)


if __package__ is None and not hasattr(sys, "frozen"):
    # direct call of __main__.py
    import os.path

    path = os.path.realpath(os.path.abspath(__file__))
    sys.path.insert(0, os.path.dirname(os.path.dirname(path)))

import nextdl

if __name__ == "__main__":
    nextdl.main()
