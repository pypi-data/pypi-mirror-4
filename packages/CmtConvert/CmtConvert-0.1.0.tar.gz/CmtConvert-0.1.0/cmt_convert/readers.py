#! /usr/bin/env python
"""
Load reader plugins
"""

from cmt_convert.plugin import (load_plugins, PLUGIN_PATH)
from cmt_convert.decorator import _ReaderPlugin


READERS = load_plugins(PLUGIN_PATH, _ReaderPlugin)
