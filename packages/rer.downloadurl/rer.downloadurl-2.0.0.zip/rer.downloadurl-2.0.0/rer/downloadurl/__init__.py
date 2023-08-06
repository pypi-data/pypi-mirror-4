# -*- coding: utf-8 -*-

import logging
from zope.i18nmessageid import MessageFactory

downloadurlMessageFactory = MessageFactory('rer.downloadurl')
logger = logging.getLogger('rer.downloadurl')

def initialize(context):
    """Initializer called when used as a Zope 2 product."""
