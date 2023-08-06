# -*- coding: utf-8 -*-

from Products.FaqAttachment import logger

def uninstall(portal, reinstall=False):
    if not reinstall:
        setup_tool = portal.portal_setup
        setup_tool.runAllImportStepsFromProfile('profile-Products.FaqAttachment:uninstall')
        logger.info("Uninstall done")