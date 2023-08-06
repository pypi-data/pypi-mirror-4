import mimetypes
import urllib
import os
import time
import transaction

from zope.interface import implements, Interface

from Acquisition import aq_inner

from zope import component
try:
    from zope.container.interfaces import INameChooser
except ImportError:
    from zope.app.container.interfaces import INameChooser

from Products.CMFCore.utils import getToolByName
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from xhostplus.gallery import galleryMessageFactory as _

try :
    #python >=2.6
    import json
except :
    #plone 3
    import simplejson as json

XHR_UPLOAD_JS = """
    var uploader = new qq.FileUploader({
        element: jq('#file_uploader')[0],
        action: '@@add_image',
        allowedExtensions: ['jpg', 'jpeg', 'png'],
        template: '<div class="qq-uploader">' +
                  '<div class="qq-upload-drop-area"><span>%(ul_draganddrop_text)s</span></div>' +
                  '<div class="qq-upload-button">%(ul_button_text)s</div>' +
                  '<ul class="qq-upload-list"></ul>' +
                  '</div>',
        fileTemplate: '<li>' +
                '<div class="qq-upload-infos"><span class="qq-upload-file"></span>' +
                '<span class="qq-upload-spinner"></span>' +
                '<span class="qq-upload-failed-text">%(ul_msg_failed)s</span></div>' +
                '<div class="qq-upload-size"></div>' +
                '<a class="qq-upload-cancel" href="#">%(ul_button_cancel)s</a>' +
            '</li>',
        messages: {
            serverError: "%(ul_error_server)s",
            alreadyExistsError: "%(ul_error_already_exists)s {file}",
            typeError: "%(ul_error_bad_ext)s {file}. %(ul_error_onlyallowed)s {extensions}.",
            sizeError: "%(ul_error_file_large)s {file}, %(ul_error_maxsize_is)s {sizeLimit}.</span>",
            emptyError: "%(ul_error_empty_file)s {file}, %(ul_error_try_again)s"
        }
    });
"""

def encode(s):
    """
    encode string
    """
    return "d".join(map(str, map(ord, s)))


def decode(s):
    """
    decode string
    """
    return "".join(map(chr, map(int, s.split("d"))))

class IAddImagesView(Interface):
    """
    add-images view interface
    """


class AddImagesView(BrowserView):
    """
    add-images browser view
    """
    implements(IAddImagesView)

    def __init__(self, context, request):
        self.context = context
        self.request = request

    @property
    def portal_catalog(self):
        return getToolByName(self.context, 'portal_catalog')

    @property
    def portal(self):
        return getToolByName(self.context, 'portal_url').getPortalObject()

class AddImagesJs(BrowserView):
    def __init__(self, context, request):
        self.context = context
        self.request = request

    def _utranslate(self, msg):
        context = aq_inner(self.context)
        return context.translate(msg, domain="xhostplus.gallery")

    def __call__(self):
        _ = self._utranslate
        strings = dict(
            ul_button_text          = _(u'Add one or more images'),
            ul_button_cancel        = _('Cancel'),
            ul_draganddrop_text     = _(u'Drag and drop images here to add'),
            ul_msg_all_sucess       = _(u'All images added with success.'),
            ul_msg_some_sucess      = _(u' images added with success, '),
            ul_msg_some_errors      = _(u" uploads return an error."),
            ul_msg_failed           = _(u"Failed"),
            ul_error_try_again      = _(u"please try again."),
            ul_error_empty_file     = _(u"This image is empty:"),
            ul_error_file_large     = _(u"This image is too large:"),
            ul_error_maxsize_is     = _(u"maximum file size is:"),
            ul_error_bad_ext        = _(u"This file has an invalid extension:"),
            ul_error_onlyallowed    = _(u"Allowed types are:"),
            ul_error_already_exists = _(u"This image already exists with the same name on server:"),
            ul_error_server         = _(u"An server error occurred."),
        )

        return XHR_UPLOAD_JS % strings

class AddImage(BrowserView):
    """ Upload an image
    """

    def _utranslate(self, msg):
        context = aq_inner(self.context)
        return context.translate(msg, domain="xhostplus.gallery")

    def _clean_filename(self, filename):
        filename, fileext = os.path.splitext(filename)
        filename = filename.replace("_", " ")
        filename = filename.capitalize()
        return filename

    def __init__(self, context, request):
        self.context = context
        self.request = request

        cookie = self.request.form.get("cookie")
        if cookie:
            self.request.cookies["__ac"] = decode(cookie)

    def __call__(self):
        _ = self._utranslate

        file_name = "unknown"
        if self.request.HTTP_X_FILE_NAME:
            file_name = urllib.unquote(self.request.HTTP_X_FILE_NAME)

        if self.request.HTTP_X_REQUESTED_WITH:
            # using ajax upload
            try:
                bodyfile = self.request.BODYFILE
                file_data = bodyfile.read()
                bodyfile.seek(0)
            except:
                return json.dumps({u'error': _(u"An unknown server error occurred")})

        file_name = self._clean_filename(file_name)

        if file_data:
            try:
                oid = self.context.invokeFactory(
                    'Image',
                    id=time.time(),
                    title=file_name,
                    image=file_data,
                    excludeFromNav=self.context.getAuto_exclude_from_nav(),
                )

                # It's necessary to save the object creation before we can rename it
                transaction.savepoint(optimistic=True)
                new_image = self.context._getOb(oid)

                oid = INameChooser(self.context).chooseName(file_name, new_image)
                new_image.setId(oid)
                new_image.reindexObject()
            except:
                return json.dumps({u'error': _(u"The file %(file)s already exists") % {'file' : file_name}})

            return json.dumps({u'success': True})
        return json.dumps({u'error': _(u"The file %(file)s is empty") % {'file' : file_name}})
