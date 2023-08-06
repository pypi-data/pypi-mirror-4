#! /usr/bin/env python
"""
Utility functions for loading plugins.
"""

import os


PLUGIN_PATH = [
    os.path.join(os.path.dirname(__file__), 'plugins')
]


def load_plugins_from_dir(path, cls):
    """
    Look for plugins in a given directory. Identify plugins as being an
    instance of the given class, cls.

    :path: Path to directory containing plugins
    :cls: Class othat defines the plugin

    :returns: A list of discovered plugins
    """
    import sys
    import imp

    plugins = {}

    sys.path.insert(0, path)
    cwd = os.getcwd()

    os.chdir(path)
    for name in os.listdir('.'):
        if os.path.isfile(name) and name.endswith('.py'):
            (mod_name, _) = os.path.splitext(name)
            mod = imp.load_module(mod_name, *imp.find_module(mod_name))
            for value in mod.__dict__.values():
                if isinstance(value, cls):
                    plugins[value.name] = value.func

    os.chdir(cwd)
    sys.path.pop(0)

    return plugins


def load_plugins(paths, cls):
    """
    Load plugins from a series of directories. Plugins found earlier in the
    search path order override those discovered later.

    :paths: A list of search paths for plugins
    :cls: Class othat defines the plugin

    :returns: A list of discovered plugins
    """
    plugins = {}
    for path in paths[::-1]:
        plugins.update(load_plugins_from_dir(path, cls))
    return plugins
