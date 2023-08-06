# -*- coding: utf-8 -*-
#
# File: setuphandlers.py
#
# Copyright (c) 2011 by Ecreall
# Generator: ArchGenXML Version 2.7
#            http://plone.org/products/archgenxml
#
# GNU General Public License (GPL)
#

__author__ = """Vincent Fretin and Michael Launay <development@ecreall.com>"""
__docformat__ = 'plaintext'


import logging
logger = logging.getLogger('cooptation: setuphandlers')
from Products.cooptation.config import PROJECTNAME
from Products.cooptation.config import DEPENDENCIES
import os
from Products.CMFCore.utils import getToolByName
import transaction
##code-section HEAD
##/code-section HEAD

def isNotcooptationProfile(context):
    return context.readDataFile("cooptation_marker.txt") is None

def setupHideToolsFromNavigation(context):
    """hide tools"""
    if isNotcooptationProfile(context): return
    # uncatalog tools
    site = context.getSite()
    toolnames = ['portal_cooptations']
    portalProperties = getToolByName(site, 'portal_properties')
    navtreeProperties = getattr(portalProperties, 'navtree_properties')
    if navtreeProperties.hasProperty('idsNotToList'):
        for toolname in toolnames:
            try:
                portal[toolname].unindexObject()
            except:
                pass
            current = list(navtreeProperties.getProperty('idsNotToList') or [])
            if toolname not in current:
                current.append(toolname)
                kwargs = {'idsNotToList': current}
                navtreeProperties.manage_changeProperties(**kwargs)



def updateRoleMappings(context):
    """after workflow changed update the roles mapping. this is like pressing
    the button 'Update Security Setting' and portal_workflow"""
    if isNotcooptationProfile(context): return
    wft = getToolByName(context.getSite(), 'portal_workflow')
    wft.updateRoleMappings()

def postInstall(context):
    """Called as at the end of the setup process. """
    # the right place for your custom code
    if isNotcooptationProfile(context): return
    site = context.getSite()



##code-section FOOT
##/code-section FOOT
