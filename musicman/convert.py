# Copyright (c) 2018 by the parties listed in the AUTHORS
# file.  All rights reserved.  Use of this source code is governed
# by a BSD-style license that can be found in the LICENSE file.

from __future__ import (absolute_import, division, print_function,
    unicode_literals)

import sys
import os
import re
import shutil

import subprocess as sp


def flac_to_alac(input, output):
    deccom = ["flac", "-s", "-d", "-f", "-c", input]
    enccom = ["ffmpeg", "-i", "-", "-loglevel", "error", "-acodec", "alac",
              output]
    dec = sp.Popen(deccom, stdin=None, stdout=sp.PIPE, stderr=None,
                   universal_newlines=True)
    enc = sp.Popen(enccom, stdin=dec.stdout, stdout=sp.PIPE, stderr=None,
                   universal_newlines=True)
    dec.stdout.close()
    out, err = enc.communicate()
    print(out)
    return


def alac_to_flac(input, output):
    deccom = ["alac-decoder", input]
    enccom = ["flac", "-s", "-o", output, "-"]
    dec = sp.Popen(deccom, stdin=None, stdout=sp.PIPE, stderr=None,
                   universal_newlines=True)
    enc = sp.Popen(enccom, stdin=dec.stdout, stdout=sp.PIPE, stderr=None,
                   universal_newlines=True)
    dec.stdout.close()
    out, err = enc.communicate()
    print(out)
    return


def convert_file(input, informat, output, outformat):
    if informat == outformat:
        shutil.copy2(input, output)
        return

    if informat == "flac":
        if outformat == "alac":
            flac_to_alac(input, output)
        else:
            raise NotImplementedError("{} --> {} unsupported".format(informat,
                outformat))
    elif informat == "alac":
        if outformat == "flac":
            alac_to_flac(input, output)
        else:
            raise NotImplementedError("{} --> {} unsupported".format(informat,
                outformat))
    elif informat == "ogg":
        raise NotImplementedError("ogg conversion not yet implemented")
    elif informat == "mp3":
        raise NotImplementedError("mp3 conversion not yet implemented")
    else:
        raise RuntimeError("Unknown format {}".format(informat))
    return
