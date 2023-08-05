# -*- coding: utf-8 -*-
#
# File: test_setup.py

__author__ = """Ramon Bartl <ramon.bartl@nexiles.de>"""
__docformat__ = 'plaintext'

import unittest

from collective.uploadify.tests.base import TestCase


class TestSetup(TestCase):
    """ Test Setup
    """

    def afterSetUp(self):
        self.setRoles(('Manager', ))

    def testViewAvailableOnPartal(self):
        self.failUnless(self.portal.restrictedTraverse('@@upload'))

    def testViewAvailableOnFolder(self):
        self.failUnless(self.folder.restrictedTraverse('@@upload'))

    def testViewNotAvailableOnContentTypes(self):
        _ = self.folder.invokeFactory("Document", "doc")
        doc = self.folder.get(_)
        self.assertFalse(doc.restrictedTraverse('@@upload', None))


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestSetup))
    return suite

# vim: set ft=python ts=4 sw=4 expandtab :
