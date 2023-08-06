# -*- coding: utf-8 -*-
from collective.zipfiletransport.utilities import interfaces as zpinterfaces
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from sc.base.uploader.testing import INTEGRATION_TESTING
from zope.component import getUtility

import os
import unittest2 as unittest


class FilenamesExportTest(unittest.TestCase):

    layer = INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.pp = self.portal['portal_properties']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        props = self.pp.sc_base_uploader
        props.manage_changeProperties(enable_export=True)
        self.portal.invokeFactory('Folder',
                                  'f1',
                                  title=u"Folder 1")
        self.folder = self.portal['f1']

    def test_import_zip(self):
        zft_util = getUtility(zpinterfaces.IZipFileTransportUtility,
                              name="sc_zipfiletransport")
        file_path = os.path.join(os.path.dirname(__file__), 'foobar.zip')
        zft_util.importContent(file=file_path,
                               context=self.folder,
                               description='test_folder zip file description',
                               contributors='test_user',
                               overwrite=False,
                               categories=[],
                               excludefromnav=False)
        folder = self.folder
        self.assertEqual(folder.objectIds(), ['foobar'])
        files = folder['foobar'].objectIds()
        self.assertTrue('test_image.png' in files)
        self.assertTrue('test_image.jpg' in files)


def test_suite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)
