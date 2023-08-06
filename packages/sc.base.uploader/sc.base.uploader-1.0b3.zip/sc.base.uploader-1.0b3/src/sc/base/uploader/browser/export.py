# -*- coding:utf-8 -*-
from Acquisition import aq_inner
from collective.zipfiletransport.utilities import interfaces as zpinterfaces
from plone.memoize import view
from Products.CMFCore.utils import getToolByName
from Products.Five import BrowserView
from zope.component import getUtility

import os


class ExportView(BrowserView):
    """ A browser view to export a folder as a zip file
    """
    def __init__(self, context, request):
        self.context = aq_inner(context)
        self.request = request
        self.zft_util = getUtility(zpinterfaces.IZipFileTransportUtility,
                                   name="sc_zipfiletransport")

    @view.memoize
    def _enable_anonymous(self):
        ''' Check if we enable anonymous download '''
        pp = getToolByName(self.context, 'portal_properties')
        sheet = pp.sc_base_uploader
        return sheet.getProperty("enable_export") or False

    def __call__(self, *args, **kwargs):
        ''' Return the zip file, if allowed '''
        # Anonymous enabled only if set globally
        pm = getToolByName(self.context, 'portal_membership')
        if (pm.isAnonymousUser() and not self._enable_anonymous()):
            return

        RESPONSE_BLOCK_SIZE = 32768
        # This would be great to filter content
        obj_paths = None

        context = self.context
        filename = '%s.zip' % (context.getId())

        zipfilename = self.zft_util.generateSafeFileName(filename)

        #Detect OS
        zipfilename = zipfilename.encode('utf-8')
        zip_path = self.zft_util.exportContent(context=self.context,
                                               obj_paths=obj_paths,
                                               filename=filename)
        response = self.context.REQUEST.RESPONSE
        response.setHeader('Cache-Control',
                           'max-age=86400, proxy-revalidate, public')
        response.setHeader('X-Cache-Rule',
                           'zip-exporsct-42')
        response.setHeader('content-type',
                           'application/zip')
        response.setHeader('content-length',
                           str(os.stat(zip_path)[6]))
        response.setHeader('Content-Disposition',
                           ' attachment; filename=' + zipfilename)

        # iterate over the temporary file object, returning it to the client
        fp = open(zip_path, 'rb')
        while True:
            data = fp.read(RESPONSE_BLOCK_SIZE)
            if data:
                self.context.REQUEST.RESPONSE.write(data)
            else:
                break
        fp.close()
        # temporary measure to see the file object...
        os.rename(zip_path, zip_path + "_TEMP")
        return
