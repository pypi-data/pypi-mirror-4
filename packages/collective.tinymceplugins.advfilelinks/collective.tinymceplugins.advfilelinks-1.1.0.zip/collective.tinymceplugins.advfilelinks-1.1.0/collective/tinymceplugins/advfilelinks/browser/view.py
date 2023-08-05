# -*- coding: utf-8 -*-

from Products.CMFCore.utils import getToolByName
from Products.Five.browser import BrowserView

from collective.tinymceplugins.advfilelinks.interfaces import IFileSuffixes

class RemoveSuffixView(BrowserView):
    """Given an URL like http://url/to/the/content/foo/bar/...
    return http://url/to/the/content
    """
    
    def __call__(self, *args, **kwargs):
        request = self.request
        portal_url = getToolByName(self.context, 'portal_url')
        portal = portal_url.getPortalObject()
        url = request.form.get('url')
        path = url.replace(portal_url(), '')
        
        obj = None
        while (obj != portal):
            obj = portal.restrictedTraverse(path[1:], default=None)
            try:
                IFileSuffixes(obj)
                return obj.absolute_url()
            except TypeError:
                pass
            
            path = '/'.join(path.split('/')[:-1])
        return url
