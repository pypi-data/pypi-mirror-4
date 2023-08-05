# -*- coding: utf-8 -*-
#
# File: adapters.py

__author__ = 'Ramon Bartl <ramon.bartl@nexiles.de>'
__docformat__ = 'plaintext'

from cStringIO import OutputType

from zope import interface
from zope import component

from plone.app.blob.interfaces import IBlobbable
from plone.app.blob.adapters.stringio import BlobbableStringIO


class BlobbablecStringIO(BlobbableStringIO):
    """ adapter for cStringIO instance to work with blobs
    """
    interface.implements(IBlobbable)
    component.adapts(OutputType)

    def __init__(self, context):
        BlobbableStringIO.__init__(self, context)

# vim: set ft=python ts=4 sw=4 expandtab :
