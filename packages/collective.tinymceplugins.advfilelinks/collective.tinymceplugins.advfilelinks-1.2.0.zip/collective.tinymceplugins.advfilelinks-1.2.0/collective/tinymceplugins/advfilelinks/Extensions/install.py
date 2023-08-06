# -*- coding: utf-8 -*-

from collective.tinymceplugins.advfilelinks import logger

def uninstall(portal, reinstall=False):
    setup_tool = portal.portal_setup
    setup_tool.runAllImportStepsFromProfile('profile-collective.tinymceplugins.advfilelinks:uninstall')
    logger.info("Uninstall done")
