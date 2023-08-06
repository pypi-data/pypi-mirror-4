.. contents:: **Table of contents**

Introduction
============

This is a plugin for `TinyMCE`__ editor for Plone.

__ http://pypi.python.org/pypi/Products.TinyMCE/

It will replace in the less obtrusive way the standard *plonelink* plugin, providing a version that
handle in a different way links to File and Image contents.

Detailed documentation
======================

When the link is not internal or not to a file nothing will change and standard Plone behavior is kept.

When you link a *file* or an *image* inside the Plone site you commonly get this XHTML code...::

    <a class="internal-link" href="my-pdf">Download the document</a>

Instead you'll get this...::

    <a class="internal-link internal-link-tofile" href="my-pdf"
       type="application/pdf" title="pdf, 146.2 kB">Download the document</a>

(the same if you have enabled "*Link using UIDs*")

The plugin also add a CSS to your Plone site that:

* Add the image icon based on file's mimetype, on the left of the link (if on IE, need IE 7 or better)
* After the linked text will be added a `text generated with CSS`__, with the same content you find in the
  *title*, put in bracket (need IE 8 or better).
  IE users with old versions still get's some additional information thanks to the *title* HTML attribute. 

__ http://www.w3.org/TR/CSS2/generate.html

.. figure:: http://blog.redturtle.it/pypi-images/collective.tinymceplugins.advfilelinks/collective.tinymceplugins.advfilelinks-1.1.0-01.png/image_preview
   :alt: Screenshot of what you see on your browser
   :target: http://blog.redturtle.it/pypi-images/collective.tinymceplugins.advfilelinks/collective.tinymceplugins.advfilelinks-1.1.0-01.png
   
   How a normal page looks like      

.. figure:: http://blog.redturtle.it/pypi-images/collective.tinymceplugins.advfilelinks/collective.tinymceplugins.advfilelinks-1.1.0-02.png/image_preview
   :alt: Screenshot of what you see in the TinyMCE generated HTML
   :target: http://blog.redturtle.it/pypi-images/collective.tinymceplugins.advfilelinks/collective.tinymceplugins.advfilelinks-1.1.0-02.png
   
   What you will find inside TinyMCE

Customize format of link to contents
------------------------------------

Plone normally doesn't manage link to file is special ways (it simply generate a link to the base URL of
the content). 

This plugin will add a new control inside advanced settings:

.. figure:: http://blog.redturtle.it/pypi-images/collective.tinymceplugins.advfilelinks/collective.tinymceplugins.advfilelinks-1.1.0-03.png/image_preview
   :alt: Advanced settings
   :target: http://blog.redturtle.it/pypi-images/collective.tinymceplugins.advfilelinks/collective.tinymceplugins.advfilelinks-1.1.0-03.png
   
   The "Link format" option, inside advanced settings

Playing with those options can change the format of the generated link, adding a suffix to it.

*Direct link to content* (TinyMCE default)
    Do not add any suffix.
*Link to content's preview* (default for *Image*)
    A link to a view of the content
*Link to download content* (default for *File*)
    Force the download of the file (or image)

Most of the time "*Link to download content*" is like "*Direct link to content*": calling ``url/to/a/file`` is like
calling ``url/to/a/file/at_download/file``, but without an explicit ``at_download/file`` sometimes the target file
can be opened by browser plugins (expecially common for images, where ``url/to/an/image`` will open the image in
the browser).

The "*Link to content' preview*" can ne used to create links that are not opening the attachment, but move user to
the Plone content.

Extending for custom contents
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Let say you are using a new Plone content type, like a Video. You want that TinyMCE links to video contents in a
custom way.

What you need is to provide a new adapter for the ``IFileSuffixes`` interface::

  <adapter
        for="your.package.content.IYourVideoType
		     zope.publisher.interfaces.browser.IHTTPRequest"
        provides="collective.tinymceplugins.advfilelinks.interfaces.IFileSuffixes"
        factory=".adapters.YourVideoTypeDownloadSuffix"
        />

The provide the Python adapter code::

	class YourVideoTypeDownloadSuffix(object):
    	implements(IFileSuffixes)
	
    	def __init__(self, context, request):
	        self.context = context
	        self.request = request
	        self.download_suffix = '/video_download'
	        self.view_suffix = '/preview_video'
	        self.default_suffix = 2

You can provide three options:

``download_suffix``
    Provide the suffix to be added when using "*Link to download content*"
    for your content.
    
    Set the value to ``None`` and no suffix wil be added or used
``view_suffix``
    Provide the suffix to be added when using "*Link to content's preview*"
    for your content.
    
    Set the value to ``None`` and no suffix wil be added or used
``default_suffix``
    Provide ad integer value to be used for settings the default combo box option.
    Use 1 for the first combo option, 2 for the second, and so on.

You can use this feature also for overriding default behavior for File and Image contents.

Dependencies
============

This product has been tested with:

* Plone 3.3.5 and TinyMCE 1.1.12
* Plone 4.2.4 and TinyMCE 1.2.15

.. Warning::
    This product will **not work** on Plone 4.3 or on every other Plone versions that use
    Products.TinyMCE 1.3 or better. Sorry... maybe in future!
    
    Why? Products.TinyMCE 1.3 has been rewritten from scratch.

Credits
=======

Developed with the support of `Regione Emilia Romagna`__;
Regione Emilia Romagna supports the `PloneGov initiative`__.

__ http://www.regione.emilia-romagna.it/
__ http://www.plonegov.it/

Authors
=======

This product was developed by RedTurtle Technology team.

.. image:: http://www.redturtle.it/redturtle_banner.png
   :alt: RedTurtle Technology Site
   :target: http://www.redturtle.it/

Thanks to the `University of Ferrara`__ for providing CSS rules to be more compatible with additional
mimetypes.

__ http://www.unife.it/



