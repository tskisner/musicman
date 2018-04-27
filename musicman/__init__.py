# Copyright (c) 2018 by the parties listed in the AUTHORS
# file.  All rights reserved.  Use of this source code is governed
# by a BSD-style license that can be found in the LICENSE file.

from ._version import get_versions
__version__ = get_versions()['version']
del get_versions

from .meta import (taglist, suffix_format, format_suffix, song_get_props,
                   song_set_props, album_props)

from .convert import (flac_to_alac, alac_to_flac, convert_file)
