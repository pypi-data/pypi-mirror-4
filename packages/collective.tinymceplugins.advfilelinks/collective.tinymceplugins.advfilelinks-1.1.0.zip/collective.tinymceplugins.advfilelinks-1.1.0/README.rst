.. contents:: **Table of contents**

Introduction
============

This is a plugin for `TinyMCE`__ editor for Plone.

__ http://plone.org/products/tinymce/

It will replace in the less obtrusive way the standard *plonelink* plugin, providing a version that
handle in a different way links to File contents.

Detailed documentation
======================

When the link is not internal or not to a file, nothing change.

When you link a *file* (or an *image*) inside the Plone site, instead of obtain this in your XHTML...::

    <a class="internal-link" href="my-pdf">Download the document</a>

...you'll get this...::

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

Playing with those options can change the format of the generated link, addind a suffix to it.

*Link to download content* (default)
    Force the download of the file (or image)
*Link to content' preview*
    A link to a view of the content
*Direct link to content* (TinyMCE default)
    Do not add any suffix. 

Most of the time "*Link to download content*" is like "*Direct link to content*".
Most of the time in Plone calling ``url/to/a/file`` is like calling ``url/to/a/file/at_download/file``, but without
an explicit ``at_download/file`` sometimes the target file can be opened by browser plugins (expecially common for
images, where ``url/to/an/image`` will open the image in the browser).

The "*Link to content' preview*" cab ne used to create links that are not opening the attachment, but move user to
the Plone content.

Dependencies
============

This product has been tested with:

* Plone 3.3.5 and TinyMCE 1.1.12
* Plone 4.2.2 and TinyMCE 1.2.12

.. Warning::
    This product will **not work** on Plone 4.3 or on other Plone sitesversions that use
    Products.TinyMCE 1.3 or better.
    
    Products.TinyMCE 1.3 has been rewritten from scratch.

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



