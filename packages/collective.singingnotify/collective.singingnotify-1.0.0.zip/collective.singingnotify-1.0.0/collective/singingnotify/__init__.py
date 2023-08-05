# -*- coding: utf-8 -*-
from zope.i18nmessageid import MessageFactory
MessageFactory = MessageFactory('collective.singingnotify')
import logging
logger = logging.getLogger('collective.singingnotify')


def initialize(context):
    """Initializer called when used as a Zope 2 product."""
