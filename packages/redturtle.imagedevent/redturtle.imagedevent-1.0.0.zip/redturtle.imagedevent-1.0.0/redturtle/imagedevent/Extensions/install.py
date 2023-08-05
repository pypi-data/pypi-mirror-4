# -*- coding: utf-8 -*-

try:
    import plone.app.collection
    NEW_COLLECTION = True
except ImportError:
    NEW_COLLECTION = False

from redturtle.imagedevent import logger


def install(portal):
    setup_tool = portal.portal_setup
    setup_tool.runAllImportStepsFromProfile('profile-redturtle.imagedevent:default')
    if NEW_COLLECTION:
        setup_tool.runAllImportStepsFromProfile('profile-redturtle.imagedevent:new-collections-support')
    logger.info("Imaged event installed")


def uninstall(portal):
    setup_tool = portal.portal_setup
    setup_tool.runAllImportStepsFromProfile('profile-redturtle.imagedevent:uninstall')
    logger.info("Ran all uninstall steps.")
