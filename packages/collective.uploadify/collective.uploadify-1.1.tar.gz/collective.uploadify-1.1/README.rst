Introduction
============

**Makes Plone File Uploads easy**

Multifileupload for Plone using uploadify_

.. _uploadify: http://www.uploadify.com


Plone integration
*****************

``Upload`` folder tab action is install with default profile. You can install
it via portal_quickinstaller or via Addons section in control panel.


Configuration
*************

The following settings can be done in the site_properties.
(please use **string** properties only!):

  - ul_auto_upload -- true/false (default: false)

    *Set to true if you would like the files to be uploaded when they are
    selected.*

  - ul_allow_multi -- true/false (default: true)

    *Set to true if you want to allow multiple file uploads.*

  - ul_sim_upload_limit -- number 1-n (default: 4)

    *A limit to the number of simultaneous uploads you would like to allow.*

  - ul_queue_size_limit -- number 1-n (default: 999)

    *A limit to the number of files you can select to upload in one go.*

  - ul_size_limit -- size in bytes (default: empty)

    *A number representing the limit in bytes for each upload.*

  - ul_file_description -- text (default: empty)

    *The text that will appear in the file type drop down at the bottom of the
    browse dialog box.*

  - ul_file_extensions -- list of extensions (default: \*.\*;)

    *A list of file extensions you would like to allow for upload.  Format like
    \*.ext1;\*.ext2;\*.ext3. FileDesc is required when using this option.*

  - ul_button_text -- text (default: BROWSE)

    *The text you would like to appear on the default button.*

  - ul_button_image -- path to image (default: empty)

    *The path to the image you will be using for the browse button.
    NOTE: If you are using a **different sized button image** you have to set
    ul_height and ul_width otherwise your ul_button_image will be stretched to
    the defaults (110x30)*

  - ul_hide_button -- true/false (default: false)

    *Set to true if you want to hide the button image.*

  - ul_script_access -- always/sameDomain (default: sameDomain)

    *The access mode for scripts in the flash file.  If you are testing locally, set to `always`.*

  - ul_width -- number (default: 110)

    *The ul_width value which should be set when using a different sized
    ul_button_image*

  - ul_height -- number (default: 30)

    *The ul_height value which should be set when using a different sized
    ul_button_image*

  - ul_scale_image_size -- x,y

    *These two values define the max x,y size in pixels of the image. Scales
    an image down to at most ul_scale_image_size size preserving aspect ratio.
    Example: 800,600 to set a maximum size of 800x600 pixels*

  - ul_content_field -- Contenttype.field

    *The uploaded file is included into the specific field from the specific Contenttype
    Example: File.file it uploads to field file from the contenttype File*



Adding a custom File Mutator Utility
************************************

If you want to so some special handling for uploaded files *before* they get
created in the portal, you can simply register a new utility providing the
IFileMutator Interface.

Your utility will be called with **file_name, file_data, content_type** just
before the content will be created in the portal.

.. sidebar:: Parameters

    **file_name**::

        type: str

        example: my-image.jpg

    **file_data**::

        type: <ZPublisher.HTTPRequest.FileUpload instance at -...>

        can be used just like a file.

    **content_type**::

        type: str

        example: 'image/jpeg'


Example
-------

A simple utility which adds a "photo-" prefix to image filenames


configure.zcml::

    <!-- An Utility to give images an "photo-" prefix -->
    <utility component=".utility.prefix_image_filename"
             name="prefix-image-filename"/>


utility.py::

    from zope import interface

    def prefix_image_filename(file_name, file_data, content_type):
        """ Prefix all images with 'photo-<filename>'
        """
        # we only handle image files
        if not content_type.startswith("image"):
            return (file_name, file_data, content_type)

        if not file_name.startswith("photo"):
            file_name = "-".join(["photo", file_name])
        return (file_name, file_data, content_type)


    interface.directlyProvides(prefix_image_filename,
                               IFileMutator)


.. note::

    Your utility has to return a tuple of::

        (file_name, file_data, content_type)


Customization for specific BrowserLayer
***************************************

If you have your own skin installed which is based on it's own BrowserLayer
(by default IThemeSpecific) and want to customize the look and feel of
collective.uploadify's you could override the upload view and/or the upload
initialize callback view

 - Customize view template::

     <configure
         xmlns="http://namespaces.zope.org/zope"
         xmlns:browser="http://namespaces.zope.org/browser">

         ...

         <!-- Customize collective.uploadify upload template -->
         <browser:page
             for="collective.uploadify.browser.interfaces.IUploadingCapable"
             name="upload"
             template="templates/upload.pt"
             permission="cmf.AddPortalContent"
             layer=".interfaces.IThemeSpecific"
             />

     </configure>

 - Customize initialize template::

    from zope.i18n import translate
    from zope.component import getMultiAdapter
    from collective.uploadify.browser.upload import UploadInitalize
    from my.product import MyMessageFactory as _


    class MyCustomUploadInitalize(UploadInitalize):
        """ Initialize uploadify js
        """

        def upload_settings(self):

            portal_state = getMultiAdapter(
                (self.context, self.request), name="plone_portal_state")

            settings = super(MyCustomUploadInitalize, self).upload_settings()
            settings.update(dict(
                ul_height = 26,
                ul_width = 105,
                ul_button_text = translate(_('Choose images'), target_language= \
                                           self.request.get('LANGUAGE', 'de')),
                ul_button_image = portal_state.navigation_root_url() + \
                    '/button_upload.png',
            ))

            return settings

   Don't forget to register the new upload initialize view for your
   themespecific browserlayer by using::

     <configure
          xmlns="http://namespaces.zope.org/zope"
          xmlns:browser="http://namespaces.zope.org/browser">

        ...

         <browser:page
             for="*"
             name="upload_initialize"
             class=".uploadify.MyCustomUploadInitalize"
             permission="cmf.AddPortalContent"
             layer=".interfaces.IThemeSpecific"
             />

     </configure>
