#!/usr/bin/env python
# encoding: utf-8
from Products.CMFCore.utils import getToolByName
import config
from c2.transform.msoffice import logger

def setupMSOfficeFile(context):
    """Add our transform in PT for MS Office"""

    site = context.getSite()
    
    # Adding our file types to MTR
    mtr = getToolByName(site, 'mimetypes_registry')
    for mt_dict in config.office_mimetypes:
        main_mt = mt_dict['mimetypes'][0]
        mt_name = mt_dict['name']
        if bool(mtr.lookup(main_mt)):
            # Already installed
            logger.info("%s (%s) Mime type already installed, skipped", main_mt, mt_name)
            continue
        mtr.manage_addMimeType(
            mt_name,
            mt_dict['mimetypes'],
            mt_dict['extensions'],
            mt_dict['icon_path'],
            binary=True,
            globs=mt_dict['globs'])
        logger.info("%s (%s) Mime type installed", main_mt, mt_name)

    # Registering our transform in PT
    transforms_tool = getToolByName(site, 'portal_transforms')
    if config.TRANSFORM_NAME not in transforms_tool.objectIds():
        # Not already installed
        transforms_tool.manage_addTransform(config.TRANSFORM_NAME, 'c2.transform.msoffice.transform')
    return


def removeMSOfficeFile(context):
    """Removing various resources from plone site"""

    # At the moment, there's no uninstall support in GenericSetup. So
    # this is run by the old style quickinstaller uninstall handler.

    site = context
    # Removing our transform from PT
    transforms_tool = getToolByName(site, 'portal_transforms')
    transforms_tool.unregisterTransform(config.TRANSFORM_NAME)
    return

