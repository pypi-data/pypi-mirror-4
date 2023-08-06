Introduction
============

Change the Plone way to generate "download" URL inside File and Image contents, putting as last item
the real filename.

How it works
============

Some statistical reporting tool like *Webtrends* (but also other) can inspect access log of a web server for
giving you informations like "how many PDF file has been downloaded".

Plone standard way of downloading File (and recently also Image) from the content view generate URLs like:

    ``http://yoursite.com/path/to/pdf_file/at_download/file``

In this case log analysis tools are not able to know that the file is a PDF.

This package simply change downalod link to something like:

    ``http://yoursite.com/path/to/pdf_file/at_download/file/realname.pdf``

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
