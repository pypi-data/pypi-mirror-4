# -*- coding: utf-8 -*-
#
# File: utility.py

__author__ = 'Ramon Bartl <ramon.bartl@nexiles.de>'
__docformat__ = 'plaintext'

import logging
from zope import interface
from zope import component
from interfaces import IFileMutator

from Products.CMFCore.utils import getToolByName
from Products.CMFCore.interfaces import ISiteRoot

try:
    # Plone > 4
    from Products.PlonePAS.utils import scale_image
except ImportError:
    # Plone < 4
    from Products.CMFPlone.utils import scale_image

logger = logging.getLogger("collective.uploadify")


def scale_image_size(file_name, file_data, content_type):
    """ Scales an image down to at most max_size preserving aspect ratio from
        an input file
    """

    # we only handle image files
    if not content_type.startswith("image"):
        return (file_name, file_data, content_type)

    # check if we have a ul_scale_image_size property
    portal = component.getUtility(ISiteRoot)
    sp = getToolByName(portal, "portal_properties").site_properties
    ul_scale_image_size = sp.getProperty('ul_scale_image_size', '')


    if ul_scale_image_size:
        # we have a property
        sizes = ul_scale_image_size.split(",")
        if len(sizes) != 2:
            logger.error("Wrong number of arguments given! "
                         "Expected: 2, Got: %s" % len(sizes))
            return (file_name, file_data, content_type)

        try:
            logger.info("Scaling down Image %s to a size of %s" % (file_name, sizes))
            new_file, mimetype = scale_image(file_data, sizes)
            file_data = new_file
        except IOError, e:
            logger.error("An error occured while trying to scale the image: %s" % str(e))

    return (file_name, file_data, content_type)


# provide the IFileMutator Interface
interface.directlyProvides(scale_image_size,
                           IFileMutator)


# ONLY FOR EXAMPLE
def prefix_filename(file_name, file_data, content_type):
    """ Prefix all images with 'photo-<filename>'
    """
    # we only handle image files
    if not content_type.startswith("image"):
        return (file_name, file_data, content_type)

    if not file_name.startswith("photo"):
        file_name = "-".join(["photo", file_name])
    return (file_name, file_data, content_type)


# provide the IFileMutator Interface
interface.directlyProvides(prefix_filename,
                           IFileMutator)

# vim: set ft=python ts=4 sw=4 expandtab :
