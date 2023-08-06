# -*- coding: utf-8 -*-

from rer.downloadurl import logger
from Products.CMFCore.utils import getToolByName

def migrateTo2000(context):
    setup_tool = getToolByName(context, 'portal_setup')
    setup_tool.runImportStepFromProfile('profile-rer.downloadurl:default', 'browserlayer')
    logger.info("Migrated to version 2.0")
