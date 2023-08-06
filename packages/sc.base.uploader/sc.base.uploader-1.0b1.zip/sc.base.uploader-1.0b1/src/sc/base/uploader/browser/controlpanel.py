# -*- coding:utf-8 -*-
from collective.quickupload.browser import quickupload_settings
from collective.zipfiletransport.browser import zipfiletransportprefs
from plone.app.controlpanel.form import ControlPanelForm
from plone.fieldsets.fieldsets import FormFieldsets
from Products.CMFCore.utils import getToolByName
from Products.CMFDefault.formlib.schema import ProxyFieldProperty
from Products.CMFDefault.formlib.schema import SchemaAdapterBase
from Products.CMFPlone.interfaces import IPloneSiteRoot
from sc.base.uploader import MessageFactory as _
from zope import schema
from zope.component import adapts
from zope.interface import Interface, implements

quickset = FormFieldsets(quickupload_settings.IQuickUploadControlPanel)
quickset.id = 'quickupload'
quickset.label = _(u'Quick Upload settings')

zipset = FormFieldsets(zipfiletransportprefs.IZipFileTransportPrefsForm)
zipset.id = 'ziptransport'
zipset.label = _(u'ZipFileTransport Settings Form')

EXPORTER_DESC = _(u'Should exporting contents from a folder be enabled '
                  u'for anonymous users?')


class IExporterPrefsForm(Interface):
    """ A configlet for exporting content. """

    enable_export = schema.Bool(title=_(u"Enable anonymous export"),
                                description=EXPORTER_DESC,
                                default=False,
                                required=False)


class ExporterCPAdapter(SchemaAdapterBase):

    adapts(IPloneSiteRoot)
    implements(IExporterPrefsForm)

    def __init__(self, context):
        super(ExporterCPAdapter, self).__init__(context)
        portal_properties = getToolByName(context, 'portal_properties')
        self.context = portal_properties.sc_base_uploader

    enable_export = ProxyFieldProperty(IExporterPrefsForm['enable_export'])

exportset = FormFieldsets(IExporterPrefsForm)
exportset.id = 'exporter'
exportset.label = _(u'Export Settings Form')


class ConfigletView(ControlPanelForm):
    """ A browser view to configure uploader
    """
    form_fields = FormFieldsets(quickset, zipset, exportset)

    label = _(u"Multiple files upload")
    description = _(u"Control settings for multiple file upload.")
    form_name = _("Multiple files upload")
