# -*- coding: utf-8 -*-
#
# File: interfaces.py

__author__ = 'Ramon Bartl <ramon.bartl@nexiles.de>'
__docformat__ = 'plaintext'

from zope import interface


class IUploadingCapable(interface.Interface):
    """ Any container/object that is supported for uploading into.
    """

class IFileMutator(interface.Interface):
    """ a file mutator utility

        returns -> (file_name, file_data, content_type)
    """

# vim: set ft=python ts=4 sw=4 expandtab :
