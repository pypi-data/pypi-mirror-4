# -*- coding: utf-8 -*-

from collective.tinymceplugins.advfilelinks import logger
from Products.CMFCore.utils import getToolByName

def migrateTo_0_2_0(context):
    setup_tool = getToolByName(context, 'portal_setup')
#    setup_tool.setBaselineContext('profile-collective.tinymceplugins.advfilelinks:to_0_2_0')
    setup_tool.runAllImportStepsFromProfile('profile-collective.tinymceplugins.advfilelinks:to_0_2_0')
    setup_tool.runImportStepFromProfile('profile-collective.tinymceplugins.advfilelinks:default', 'browserlayer')
    logger.info("Migrated to version 0.2")
