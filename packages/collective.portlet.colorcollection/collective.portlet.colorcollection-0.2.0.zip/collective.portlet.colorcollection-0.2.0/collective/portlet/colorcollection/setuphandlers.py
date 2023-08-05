# -*- coding: utf-8 -*-

from Products.CMFCore.utils import getToolByName

def setupVarious(context):
    if context.readDataFile('collective.portlet.colorcollection_various.txt') is None:
        return

