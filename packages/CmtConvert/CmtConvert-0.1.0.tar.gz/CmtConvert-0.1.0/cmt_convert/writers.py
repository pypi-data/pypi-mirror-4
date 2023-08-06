#! /usr/bin/env python
"""
Load writer plugins.
"""
from cmt_convert.plugin import (load_plugins, PLUGIN_PATH)
from cmt_convert.decorator import _WriterPlugin


WRITERS = load_plugins(PLUGIN_PATH, _WriterPlugin)
