#!/usr/bin/env python3
from __future__ import unicode_literals

import os
import sys
import textwrap

# We must be able to import nextdl
sys.path.insert(
    0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)

import nextdl


def main():
    with open("supportedsites.html.in", "r", encoding="utf-8") as tmplf:
        template = tmplf.read()

    ie_htmls = []
    for ie in nextdl.list_extractors(age_limit=None):
        ie_html = "<b>{}</b>".format(ie.IE_NAME)
        ie_desc = getattr(ie, "IE_DESC", None)
        if ie_desc is False:
            continue
        elif ie_desc is not None:
            ie_html += ": {}".format(ie.IE_DESC)
        if not ie.working():
            ie_html += " (Currently broken)"
        ie_htmls.append("<li>{}</li>".format(ie_html))

    template = template.replace("@SITES@", textwrap.indent("\n".join(ie_htmls), "\t"))

    with open("supportedsites.html", "w", encoding="utf-8") as sitesf:
        sitesf.write(template)


if __name__ == "__main__":
    main()
