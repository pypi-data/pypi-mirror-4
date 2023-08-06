#! /usr/bin/env python
"""
Some utility function for this package.
"""

import os


def _get_next_name_in_sequence(name):
    """
    Get the next file name based on a base name. If a file exists with the
    given name, append an underscore to the base name followed by an integer.
    Start with 0 and increment by 1 until finding a unique file name.

    :name: Filename

    :returns: Next unique filename 
    """
    (root, ext) = os.path.splitext(name)

    file_exists = os.path.isfile(name)
    i = 0
    while file_exists:
        name = root + '_%d' % i + ext
        file_exists = os.path.isfile(name)
        i += 1

    return name
