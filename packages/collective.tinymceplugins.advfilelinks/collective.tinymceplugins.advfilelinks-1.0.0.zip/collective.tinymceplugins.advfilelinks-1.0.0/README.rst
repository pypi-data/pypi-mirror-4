Introduction
============

This is a plugin for `TinyMCE`__ editor for Plone.

__ http://plone.org/products/tinymce/

It will replace in the less obtrusive way the standard *plonelink* plugin, providing a version that
handle in a different way links to File contents.

When the link is not internal or not to a file, nothing change.

When you link a file inside the Plone site, instead of obtain this in your XHTML...::

    <a class="internal-link" href="./my-pdf">Download the document</a>

...you'll get this...::

    <a class="internal-link internal-link-tofile" href="./my-pdf"
       type="application/pdf" title="pdf, 146.2 kB">Download the document</a>

The plugin also add a CSS to your Plone site that:

* Add the image icon based on file's mimetype, on the left of the link (if on IE, need IE 7 or better)
* After the linked text will be added a `text generated with CSS`__, with the same content you find in the
  *title*, put in bracket (need IE 8 or better).
  IE users with old versions still get's some additional information thanks to the *title* attribute. 

__ http://www.w3.org/TR/CSS2/generate.html

.. figure:: http://keul.it/images/plone/collective.tinymceplugins.advfilelinks-0.0.1-01.png
   :alt: Screenshot of what you see on Firefox      

   How this looks like (on Firefox)      

.. figure:: http://keul.it/images/plone/collective.tinymceplugins.advfilelinks-0.0.1-02.png
   :alt: Screenshot of what you see in the TinyMCE XHML generated
     
   What you will find inside TinyMCE

Dependencies
------------

This product has been tested with:

* Plone 3.3.5 and TinyMCE 1.1.12
* Plone 4.1.4 and TinyMCE 1.2.10

TODO
====

* More control on the plugin popup on what the user can show when creating the link

Credits
=======

Developed with the support of `Regione Emilia Romagna`__; Regione Emilia Romagna supports the `PloneGov initiative`__.

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



