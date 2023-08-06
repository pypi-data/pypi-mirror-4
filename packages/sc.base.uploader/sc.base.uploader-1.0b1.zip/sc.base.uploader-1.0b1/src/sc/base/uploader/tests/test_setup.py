# -*- coding: utf-8 -*-

from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from sc.base.uploader.config import PROJECTNAME
from sc.base.uploader.testing import INTEGRATION_TESTING

import unittest2 as unittest

CSS = [
    "++resource++uploader.css",
]


class InstallTest(unittest.TestCase):

    layer = INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']

    def test_installed(self):
        qi = getattr(self.portal, 'portal_quickinstaller')
        self.assertTrue(qi.isProductInstalled(PROJECTNAME))

    def test_dependencies_installed(self):
        qi = getattr(self.portal, 'portal_quickinstaller')
        self.assertTrue(qi.isProductInstalled('collective.quickupload'))
        self.assertTrue(qi.isProductInstalled('collective.zipfiletransport'))

    def test_cssregistry(self):
        portal_css = self.portal.portal_css
        for css_file in CSS:
            self.assertTrue(css_file in portal_css.getResourceIds(),
                            '%s not installed' % css_file)


class UninstallTest(unittest.TestCase):

    layer = INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        self.qi = getattr(self.portal, 'portal_quickinstaller')
        self.qi.uninstallProducts(products=[PROJECTNAME])

    def test_uninstalled(self):
        self.assertFalse(self.qi.isProductInstalled(PROJECTNAME))

    def test_cssregistry_removed(self):
        portal_css = self.portal.portal_css
        for css_file in CSS:
            self.assertFalse(css_file in portal_css.getResourceIds(),
                             '%s not installed' % css_file)


def test_suite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)
