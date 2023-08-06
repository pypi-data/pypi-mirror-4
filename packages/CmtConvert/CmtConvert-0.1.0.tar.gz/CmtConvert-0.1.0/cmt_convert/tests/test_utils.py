#! /usr/bin/env python
"""
Unit tests for cmt_convert._utils
"""

import os
import unittest

from cmt_convert._utils import _get_next_name_in_sequence


class TestNextFileInSequence(unittest.TestCase):
    """
    Unit test for cmt_convert._utils._get_next_name_in_sequence.
    """
    def test_no_file(self):
        """
        The file name is already unique.
        """
        name = _get_next_name_in_sequence('base.ext')

        self.assertEqual(name, 'base.ext')

    def test_file_exists(self):
        """
        The file name already exists. Append "_0" to it's base.
        """
        import tempfile

        (_, unique_name) = tempfile.mkstemp(suffix='.ext', dir=os.getcwd())

        name = _get_next_name_in_sequence(unique_name)

        (unique_base, _) = os.path.splitext(unique_name)
        self.assertEqual(name, unique_base + '_0.ext')

        os.remove(unique_name)


if __name__ == '__main__':
    unittest.main()
