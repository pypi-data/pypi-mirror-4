# -*- coding: utf-8 -*-

from Products.CMFCore.utils import getToolByName

import logging
PROFILE_ID = 'profile-redturtle.imagedevent:default'

def addKeyToCatalog(portal, logger=None):
    '''Takes portal_catalog and adds a key to it
    @param portal: context providing portal_catalog
    '''
    if logger is None:
        # Called as upgrade step: define our own logger.
        logger = logging.getLogger('redturtle.imagedevent')

    catalog = getToolByName(portal, 'portal_catalog')
    indexes = catalog.indexes()
    # Specify the indexes you want, with ('index_name', 'index_type')
    wanted = (('getEventType', 'KeywordIndex'),
              )

    indexables = []
    for name, meta_type in wanted:
        if name not in indexes:
            catalog.addIndex(name, meta_type)
            indexables.append(name)
            logger.info("Added %s for field %s.", meta_type, name)
    if len(indexables) > 0:
        logger.info("Indexing new indexes %s.", ', '.join(indexables))
        catalog.manage_reindexIndex(ids=indexables)

def setupVarious(context):
    logger = context.getLogger('redturtle.imagedevent')
    portal = context.getSite()
    
    if context.readDataFile('redturtle.imagedevent_various.txt') is None: 
        return
    
    addKeyToCatalog(portal, logger)


def migrateTo06(context):
    """Method to separate keywords by type of event.
    This method is used as upgrade step, 'context' is portal_setup."""
    
    logger=logging.getLogger('redturtle.imagedevent')
    
    brains = context.portal_catalog(portal_type="Event")
    
    for brain in brains:
        event_obj=brain.getObject()
        event_obj.setSubject('')
        event_obj.reindexObject(idxs=['Subject'])
    
    logger.info("Remove keywords 'type of event' from the categories.")

def migrateTo100rc1(context, logger=None):
    if logger is None:
        logger = logging.getLogger('redturtle.imagedevent')
    setup_tool = getToolByName(context, 'portal_setup')
    setup_tool.runImportStepFromProfile(PROFILE_ID, 'typeinfo')
    addKeyToCatalog(context, logger)
    logger.info("Migrated to 1.0.0rc1")

def migrateTo1000(context, logger=None):
    if logger is None:
        logger = logging.getLogger('redturtle.imagedevent')
    setup_tool = getToolByName(context, 'portal_setup')
    setup_tool.runImportStepFromProfile(PROFILE_ID, 'typeinfo')
    logger.info("Migrated to 1.0.0")
