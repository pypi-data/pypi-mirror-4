# -*- coding: utf-8 -*-

from elementtree import HTMLTreeBuilder

try:
    import json
except:
    import simplejson as json

from zope.interface import implements
from zope.component import getUtility
from zope.component import queryMultiAdapter

from Products.TinyMCE.interfaces.utility import ITinyMCE
from Products.TinyMCE.adapters.interfaces.JSONDetails import IJSONDetails

from collective.tinymceplugins.advfilelinks.interfaces import IFileSuffixes

class JSONDetails(object):
    """Return details of the current object in JSON"""
    implements(IJSONDetails)

    def __init__(self, context):
        self.context = context

    def getDetails(self):
        """Builds a JSON object based on the details
           of this object.
        """

        context = self.context
        utility = getUtility(ITinyMCE)
        anchor_portal_types = utility.containsanchors.split('\n')
        image_portal_types = utility.imageobjects.split('\n')

        results = {}
        results['title'] = context.title_or_id()
        results['description'] = context.Description()

        if context.portal_type in image_portal_types:
            results['thumb'] = context.absolute_url() + "/image_thumb"
            results['scales'] = utility.getImageScales(context.getPrimaryField())
        else:
            results['thumb'] = ""

        if context.portal_type in anchor_portal_types:
            results['anchors'] = []
            tree = HTMLTreeBuilder.TreeBuilder()
            tree.feed('<root>%s</root>' % context.getText())
            rootnode = tree.close()
            for x in rootnode.getiterator():
                if x.tag == "a":
                    if "name" in x.keys():
                        results['anchors'].append(x.attrib['name'])
        else:
            results['anchors'] = []
        
        filename = context.getFilename()
        if filename.find(".")>-1:
            extension = filename.split(".")[-1]
        else:
            extension = ''
        results['content_type'] = context.content_type
        results['size'] = context.getObjSize()
        results['extension'] = extension

        suffix_provider = queryMultiAdapter((context, context.REQUEST), interface=IFileSuffixes)
        results['suffixes'] = {}
        results['suffixes']['download'] = suffix_provider and suffix_provider.download_suffix or None
        results['suffixes']['view'] = suffix_provider and suffix_provider.view_suffix or '/view'
        results['suffixes']['default_suffix'] = suffix_provider and suffix_provider.default_suffix or 1

        return json.dumps(results)


class ATFileDownloadSuffix(object):
    implements(IFileSuffixes)
    
    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.download_suffix = '/at_download/file'
        self.view_suffix = None
        self.default_suffix = 2


class ATImageDownloadSuffix(object):
    implements(IFileSuffixes)
    
    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.download_suffix = '/at_download/image'
        self.view_suffix = '/image_view_fullscreen'
        self.default_suffix = 3
