# -*- coding: utf-8 -*-

from rer.downloadurl import logger

def uninstall(portal, reinstall=False):
    setup_tool = portal.portal_setup
    setup_tool.runAllImportStepsFromProfile('profile-rer.downloadurl:uninstall')
    logger.info("Uninstall done")
