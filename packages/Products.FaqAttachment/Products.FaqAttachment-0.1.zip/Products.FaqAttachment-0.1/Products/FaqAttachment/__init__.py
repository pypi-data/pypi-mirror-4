# -*- coding: utf-8 -*-

import logging

from zope.i18nmessageid import MessageFactory

messageFactory = MessageFactory('Products.FaqAttachment')
logger = logging.getLogger('Products.FaqAttachment')


def initialize(context):
    """Initializer called when used as a Zope 2 product."""
