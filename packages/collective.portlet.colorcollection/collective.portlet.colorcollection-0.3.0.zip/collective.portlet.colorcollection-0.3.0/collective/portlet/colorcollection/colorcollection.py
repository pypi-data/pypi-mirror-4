# -*- coding: utf-8 -*-

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from plone.portlet.collection.collection import Renderer

class ColorCollectionRenderer(Renderer):

    _template = ViewPageTemplateFile('colorcollection.pt')
    render = _template
