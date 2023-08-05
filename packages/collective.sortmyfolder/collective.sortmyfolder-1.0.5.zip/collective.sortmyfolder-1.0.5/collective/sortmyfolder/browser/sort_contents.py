# -*- coding: utf-8 -*-

from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile


class SortContentsView(BrowserView):
    """The view for sorting folders"""

    template = ViewPageTemplateFile("sort_contents.pt")

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.request.set('disable_border', True)

    def __call__(self, *args, **kw):
        return self.template()
