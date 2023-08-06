# -*- coding:utf-8 -*-
from Acquisition import aq_base
from Acquisition import aq_inner
from plone.app.contentmenu.menu import FactoriesMenu
from sc.base.uploader import MessageFactory as _


class CustomMenu(FactoriesMenu):
    """
    Custom menu
    """

    def getMenuItems(self, context, request):
        # menuitems is a list of tal-friendly dictionaries
        menuitems = super(CustomMenu, self).getMenuItems(context, request)
        base_context = aq_base(aq_inner(context))
        if bool((getattr(base_context, 'isPrincipiaFolderish', False) or
                context.portal_type == 'Plone Site')):
            url = context.absolute_url()
            new_menu = {'extra': {'separator': None,
                                  'id': 'multiple-files',
                                  'class': 'contenttype-multiple-files'},
                        'submenu': None,
                        'description': _(u'A form to upload multiple files.'),
                        'title': _(u'Multiple Files'),
                        'action': '%s/@@mass-import' % url,
                        'selected': False,
                        'id': 'Multiple Files',
                        'icon': None}
            menuitems.insert(-1, new_menu)

        return menuitems
