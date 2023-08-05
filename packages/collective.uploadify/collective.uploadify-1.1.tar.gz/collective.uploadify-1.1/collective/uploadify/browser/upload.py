# -*- coding: utf-8 -*-
#
# File: upload.py

__author__ = 'Ramon Bartl <ramon.bartl@nexiles.de>'
__docformat__ = 'plaintext'

import logging
import mimetypes

from Acquisition import aq_inner

from zope import component
from zope.filerepresentation.interfaces import IFileFactory

from Products.CMFCore.utils import getToolByName
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.i18n.normalizer.interfaces import IIDNormalizer

from interfaces import IFileMutator

logger = logging.getLogger("collective.uploadify")


def encode(s):
    """ encode string
    """

    return "d".join(map(str, map(ord, s)))


def decode(s):
    """ decode string
    """

    return "".join(map(chr, map(int, s.split("d"))))


# NOTE, THIS IS NOT A PYTHON DICT:
# NEVER ADD A COMMA (,) AT THE END OF THE LAST KEY/VALUE PAIR, THIS BREAKS ALL
# M$ INTERNET EXPLORER
UPLOAD_JS = """
    function all_complete(event, data) {
        //alert(data.filesUploaded + " Files Uploaded!");
        //alert(data.errors + " Errors");
        //alert(data.speed + " Avg. Speed");
        location.reload();
    };
    jq(document).ready(function() {
        jq('#uploader').uploadify({
            'uploader'      : '++resource++uploader.swf',
            'script'        : '@@upload_file',
            'cancelImg'     : '++resource++cancel.png',
            'height'        : '%(ul_height)s',
            'width'         : '%(ul_width)s',
            'folder'        : '%(physical_path)s',
            'scriptData'    : {'cookie': '%(cookie)s'},
            'onAllComplete' : all_complete,
            'auto'          : %(ul_auto_upload)s,
            'multi'         : %(ul_allow_multi)s,
            'simUploadLimit': '%(ul_sim_upload_limit)s',
            'queueSizeLimit': '%(ul_queue_size_limit)s',
            'sizeLimit'     : '%(ul_size_limit)s',
            'fileDesc'      : '%(ul_file_description)s',
            'fileExt'       : '%(ul_file_extensions)s',
            'buttonText'    : '%(ul_button_text)s',
            'buttonImg'     : '%(ul_button_image)s',
            'scriptAccess'  : '%(ul_script_access)s',
            'hideButton'    : %(ul_hide_button)s
        });
    });
"""


def generate_id(container, title):
    """ Generates a uniqe id from a specific title
    """
    normalizer = component.getUtility(IIDNormalizer)
    obj_id = normalizer.normalize(title)
    if hasattr(container, obj_id):
        obj_id = container.generateUniqueId(obj_id)

    return obj_id


class UploadView(BrowserView):
    """ The Upload View
    """

    template = ViewPageTemplateFile("upload.pt")

    def __call__(self):
        return self.template()


class UploadFile(BrowserView):
    """ Upload a file
    """

    def __init__(self, context, request):
        self.context = context
        self.request = request

        cookie = self.request.form.get("cookie")
        if cookie:
            self.request.cookies["__ac"] = decode(cookie)

    def __call__(self):
        file_name = self.request.form.get("Filename", "")
        # ZPublisher.HTTPRequest.FileUpload instance
        file_data = self.request.form.get("Filedata", None)
        content_type = mimetypes.guess_type(file_name)[0] or ""

        # call all file mutator utilities
        for mutator in component.getAllUtilitiesRegisteredFor(IFileMutator):
            file_name, file_data, content_type = mutator(file_name, file_data, content_type)

        if not file_data:
            return

        logger.info("uploading file: filename=%s, content_type=%s" % \
                (file_name, content_type))

        sp = getToolByName(self.context, "portal_properties").site_properties
        ul_content_field = sp.getProperty('ul_content_field', '')

        if not ul_content_field:
            factory = IFileFactory(self.context)
            f = factory(file_name, content_type, file_data)
        else:
            fields = ul_content_field.split('.')
            obj_id = generate_id(self.context, file_name)
            param = {
                    'type_name': fields[0],
                    'id': obj_id,
                    fields[1]: file_data,
            }
            self.context.invokeFactory(**param)
            f = self.context[obj_id]

        logger.info("file url: %s" % f.absolute_url())
        return f.absolute_url()


class UploadInitalize(BrowserView):
    """ Initialize uploadify js
    """

    def __init__(self, context, request):
        super(UploadInitalize, self).__init__(context, request)
        self.context = aq_inner(context)

    def upload_settings(self):
        sp = getToolByName(self.context, "portal_properties").site_properties
        portal_url = getToolByName(self.context, 'portal_url')()

        settings = dict(
            cookie              = self.request.cookies.get('__ac', ''),
            portal_url          = portal_url,
            context_url         = self.context.absolute_url(),
            physical_path       = "/".join(self.context.getPhysicalPath()),
            ul_height           = sp.getProperty('ul_height', '30'),
            ul_width            = sp.getProperty('ul_width', '110'),
            ul_auto_upload      = sp.getProperty('ul_auto_upload', 'false'),
            ul_allow_multi      = sp.getProperty('ul_allow_multi', 'true'),
            ul_sim_upload_limit = sp.getProperty('ul_sim_upload_limit', 4),
            ul_queue_size_limit = sp.getProperty('ul_queue_size_limit', 999),
            ul_size_limit       = sp.getProperty('ul_size_limit', ''),
            ul_file_description = sp.getProperty('ul_file_description', ''),
            ul_file_extensions  = sp.getProperty('ul_file_extensions', '*.*;'),
            ul_button_text      = sp.getProperty('ul_button_text', 'BROWSE'),
            ul_button_image     = sp.getProperty('ul_button_image', ''),
            ul_hide_button      = sp.getProperty('ul_hide_button', 'false'),
            ul_script_access    = sp.getProperty('ul_script_access', 'sameDomain'),
        )

        # This encoding is needed when the cookie value contains spaces!
        settings["cookie"] = encode(settings["cookie"])

        return settings

    def __call__(self):
        settings = self.upload_settings()
        return UPLOAD_JS % settings

# vim: set ft=python ts=4 sw=4 expandtab :
