# -*- coding:utf-8 -*-
from zope.interface import implements
from Products.CMFQuickInstallerTool import interfaces as qi_interfaces
from Products.CMFPlone import interfaces as plone_interfaces


class HiddenProducts(object):
    implements(qi_interfaces.INonInstallable)

    def getNonInstallableProducts(self):
        return []
#        return [u'collective.quickupload',
#                u'collective.zipfiletransport']


class HiddenProfiles(object):
    implements(plone_interfaces.INonInstallable)

    def getNonInstallableProfiles(self):
        return [u'sc.base.uploader:uninstall']
#        return [u'collective.quickupload:default',
#                u'collective.zipfiletransport:default']
