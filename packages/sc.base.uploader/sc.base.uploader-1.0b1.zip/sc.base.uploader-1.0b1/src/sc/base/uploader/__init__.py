# -*- coding: utf-8 -*-
from sc.base.uploader import patch
from zope.i18nmessageid import MessageFactory as BaseMessageFactory

MessageFactory = BaseMessageFactory('sc.base.uploader')


def initialize(context):
    """Initializer called when used as a Zope 2 product."""


patch.run()
