# -*- coding: utf-8 -*-

from zope.interface import implements
from zope.component import adapts
from zope.component import getUtility
from Products.TinyMCE.interfaces.utility import ITinyMCE
from Products.TinyMCE.adapters.interfaces.JSONDetails import IJSONDetails
from Products.CMFCore.interfaces._content import IContentish, IFolderish
from Products.CMFPlone.interfaces.siteroot import IPloneSiteRoot
from Products.CMFCore.utils import getToolByName
from Acquisition import aq_inner
from elementtree import HTMLTreeBuilder

try:
    import json
except:
    import simplejson as json

class JSONDetails(object):
    """Return details of the current object in JSON"""
    implements(IJSONDetails)

    def __init__(self, context):
        """Constructor"""
        self.context = context

    def getDetails(self):
        """Builds a JSON object based on the details
           of this object.
        """

        utility = getUtility(ITinyMCE)
        anchor_portal_types = utility.containsanchors.split('\n')
        image_portal_types = utility.imageobjects.split('\n')

        results = {}
        results['title'] = self.context.title_or_id()
        results['description'] = self.context.Description()

        if self.context.portal_type in image_portal_types:
            results['thumb'] = self.context.absolute_url() + "/image_thumb"
            results['scales'] = utility.getImageScales(self.context.getPrimaryField())
        else:
            results['thumb'] = ""

        if self.context.portal_type in anchor_portal_types:
            results['anchors'] = []
            tree = HTMLTreeBuilder.TreeBuilder()
            tree.feed('<root>%s</root>' % self.context.getText())
            rootnode = tree.close()
            for x in rootnode.getiterator():
                if x.tag == "a":
                    if "name" in x.keys():
                        results['anchors'].append(x.attrib['name'])
        else:
            results['anchors'] = []
        
        filename = self.context.getFilename()
        if filename.find(".")>-1:
            extension = filename.split(".")[-1]
        else:
            extension = ''
        results['content_type'] = self.context.content_type
        results['size'] = self.context.getObjSize()
        results['extension'] = extension

#        jsonWriter = getUtility(interfaces.IJSONWriter)
#        return jsonWriter.write(results)
        return json.dumps(results)
