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

import os
import subprocess

from ..utils import check_executable, encodeFilename
from .common import FileDownloader


class RtspFD(FileDownloader):
    def real_download(self, filename, info_dict):
        url = info_dict["url"]
        self.report_destination(filename)
        tmpfilename = self.temp_name(filename)

        if check_executable("mplayer", ["-h"]):
            args = [
                "mplayer",
                "-really-quiet",
                "-vo",
                "null",
                "-vc",
                "dummy",
                "-dumpstream",
                "-dumpfile",
                tmpfilename,
                url,
            ]
        elif check_executable("mpv", ["-h"]):
            args = [
                "mpv",
                "-really-quiet",
                "--vo=null",
                "--stream-dump=" + tmpfilename,
                url,
            ]
        else:
            self.report_error(
                'MMS or RTSP download detected but neither "mplayer" nor "mpv" could be run. Please install any.'
            )
            return False

        self._debug_cmd(args)

        retval = subprocess.call(args)
        if retval == 0:
            fsize = os.path.getsize(encodeFilename(tmpfilename))
            self.to_screen("\r[%s] %s bytes" % (args[0], fsize))
            self.try_rename(tmpfilename, filename)
            self._hook_progress(
                {
                    "downloaded_bytes": fsize,
                    "total_bytes": fsize,
                    "filename": filename,
                    "status": "finished",
                }
            )
            return True
        else:
            self.to_stderr("\n")
            self.report_error("%s exited with code %d" % (args[0], retval))
            return False
