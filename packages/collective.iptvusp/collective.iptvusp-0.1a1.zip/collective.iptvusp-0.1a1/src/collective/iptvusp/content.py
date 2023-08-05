# -*- coding: utf-8 -*-
from five import grok
from plone.directives import dexterity, form

from collective.iptvusp.config import BASE_EMBED
from collective.iptvusp.config import BASE_URL
from collective.iptvusp.config import EMBED

grok.templatedir('templates')


class IUSPVideo(form.Schema):
    """
    A video from the IPTV USP Service
    """
    form.model("models/uspvideo.xml")


# FIXME: we must inherit from dexterity.Item but we have to fix issue #48
class USPVideo(dexterity.Item):
    """
    """
    grok.implements(IUSPVideo)


class View(grok.View):
    grok.context(IUSPVideo)
    grok.require('zope2.View')
    grok.name('view')

    @property
    def width(self):
        return self.context.width

    @property
    def height(self):
        return self.context.height

    def cooked_source(self):
        url = self.context.remote_url
        return url.replace(BASE_URL, BASE_EMBED)

    def embed(self):
        ''' Return the code to be embedded '''
        params = {}
        params['width'] = self.width
        params['height'] = self.height
        params['src'] = self.cooked_source()
        return EMBED % params
