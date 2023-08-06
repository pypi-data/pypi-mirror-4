# -*- coding: utf-8 -*-

from zope.interface import Interface
from zope.interface import Attribute

class IFileSuffixes(Interface):
    """An object able to provide a download_suffix and a view_suffix attribute.
    
    Those attributes are used to know what is the best way to manage a content from TinyMCE
    """
    
    download_suffix = Attribute("""Download suffix to be used for generate a download link to this content""")
    view_suffix = Attribute("""View suffix to be used for generate a preview link to this content""")
    default_suffix = Attribute("""Default view suffix to be used""")

