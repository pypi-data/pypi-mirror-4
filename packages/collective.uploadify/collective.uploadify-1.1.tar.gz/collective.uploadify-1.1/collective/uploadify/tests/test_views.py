# -*- coding: utf-8 -*-
#
# File: test_views.py

__author__    = """Ramon Bartl <ramon.bartl@nexiles.de>"""
__docformat__ = 'plaintext'

import unittest

from collective.uploadify.tests.base import TestCase


class TestViews(TestCase):
    """ Test View Class
    """

    def afterSetUp(self):
        self.setRoles(('Manager', ))


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestViews))
    return suite

# vim: set ft=python ts=4 sw=4 expandtab :
