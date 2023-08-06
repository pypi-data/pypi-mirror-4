#! /usr/bin/env python
"""
Unit tests for cmt.bmi.checker
"""

import unittest

from cmt.bmi.checker import split_type_string


class TestSplitTypeString(unittest.TestCase): #pylint:disable-msg=R0904
    """
    Unit tests for utility functions in cmt.bmi.checker
    """
    def test_one_generation(self):
        """
        Split type strings without children.
        """
        (parent, child) = split_type_string('list')

        self.assertEqual(parent, 'list')
        self.assertEqual(child, '')

    def test_two_generations(self):
        """
        Split type strings with one child.
        """
        (parent, child) = split_type_string('list:str')

        self.assertEqual(parent, 'list')
        self.assertEqual(child, 'str')

    def test_three_generations(self):
        """
        Split type strings with child and grandchild.
        """
        (parent, child) = split_type_string('list:tuple:int')

        self.assertEqual(parent, 'list')
        self.assertEqual(child, 'tuple:int')


if __name__ == '__main__':
    unittest.main()
