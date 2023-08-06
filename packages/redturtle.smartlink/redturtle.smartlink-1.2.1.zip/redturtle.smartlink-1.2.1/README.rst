.. contents:: **Table of contents**

Introduction
============

An enhanced version of the base Plone link content type.

After installing this you'll see that the Plone link will have a new *image* and *caption* fields
like the News Item content type.

.. image:: http://keul.it/images/plone/redturtle.smartlink-1.0.0rc2-1.png
   :alt: Advanced fields tab

Also the new Link type can handle internal (to Plone contents) and external links. You can use the
internal link field to automatically attach the link value to an internal content of the portal
(in a similar way used for related contents).

.. image:: http://keul.it/images/plone/redturtle.smartlink-1.0.0rc2-2.png
   :alt: The Smart Link edit form

An event-based system will also keep URLs updated even when you move/rename target document.

You can also customize the link icon for being able to use a different icon from the default Plone ones.
Due to changes between Plone 3 and Plone 4 themes, we need to keep the Plone 3 approach for displaying icons
(not using CSS sprite. To restore the Plone 4 default way, disable the ``smart_link.css`` resource
and remove the "*Icon (Expression)*" value from ``portal_types`` tool).

Handle back-end/front-end URLs
------------------------------

The Smart Link structure is nothing more that a ATLink content, so the way used to store URL
in the object or in the site's catalog is the same as Plone. There is no magic behind.

For this reason, when you are using Smart Link for internal references, the *static* URL is
stored and used.

This will lead to problems when you are using this product for site where you have different
back-end/front-end URLs; those problems are the same you have when you don't use this product!

For this reason you must use the "*Configure Smart Link*" control panel to handle URL transformation.

.. image:: http://keul.it/images/plone/redturtle.smartlink-1.0.0rc2-3.png
   :alt: The 'Configure Smart Link' panel

You can also use an option that says to Smart Link to store relative URLs, but this will also
include the Plone site id in every link (and you must rewrite this from Apache if you don't
like this). 

Blob and Blob migration tool
----------------------------

SmartLink supports (starting from 1.0.0 revision) the use of blob for the image field.
In this way we doesn't increases the size of Data.fs .

The Blob support for SmartLink is activated only if `plone.app.blob`__ is installed.
Plone 4 has Blob as storage default for the images and the files.
On Plone 3.x you have to install it by yourself.

__ http://pypi.python.org/pypi/plone.app.blob

If you have already created Smark Link contents with an old version that doesn't support Blobs
you have to launch a migration utility from the Smart Link control panel. 

E.g.: http://myhost/@@blob-smartlink-migration

Migrate ATLink to Smart Link (and back)
---------------------------------------

Smart Link contains two Generic Setup import steps that can help you to transform all you ATLink
to Smart Link, or to go back to ATLink if you don't like Smart Link anymore (automatically done
when you uninstall the product).

Warning 1
---------

Smart Link shape-change itself to be the Link content type, and hide the basic Plone Link type. Old ATLink
already created will continue working normally, but only new created link will behave the Smart Link
features.

Warning 2
---------

**Pay attention** when you update the whole portal_catalog using ZMI from URLs different from
back-end or front-end ones (for example: using a SSH tunnel).

If you run the update from (for example) "localhost:8090/site" and this URL is not the public
or one of the back-end URLs, all your internal links will be changed to this hostname!
Another catalog update (from the right URL) will fix this.

Safe re-install, clean uninstall
--------------------------------

You can *re-install* Smart Link safely for upgrade task or for restore changes, without any problem.

If you *uninstall* it, all data from Smart Link will be removed. This means that if you re-install
it after all your internal links will not be linked to target contents.

Requirements
============

Smart Link has been tested on:

* Plone 3.3
* Plone 4.2 
* Plone 4.3

Plone 3 notes
-------------

There's some kwno issues for this product on Plone 3.3:

* uninstall will probably not work (you can try to add to your buildout `experimental.backportGS`__)
* uninstall will restore the Plone 4 style Link
* you must manually activate `plone.app.imaging`__ in your Plone site

__ http://pypi.python.org/pypi/experimental.backportGS
__ http://pypi.python.org/pypi/plone.app.imaging

Additional documentation
========================

You can find more documentation on the `project's home page`__

__ http://plone.org/products/smart-link/documentation/

Credits
=======

Developed with the support of:

* `Camera di Commercio di Ferrara`__
  
  .. image:: http://www.fe.camcom.it/cciaa-logo.png/
     :alt: CCIAA Ferrara - logo
  
* `Regione Emilia Romagna`__
* `Azienda USL Ferrara`__
  
  .. image:: http://www.ausl.fe.it/logo_ausl.gif
     :alt: Azienda USL - logo

* `Rete Civica Mo-Net - Comune di Modena`__
  
  .. image:: http://www.comune.modena.it/grafica/logoComune/logoComunexweb.jpg 
     :alt: Comune di Modena - logo

All of them supports the `PloneGov initiative`__.

__ http://www.fe.camcom.it/
__ http://www.regione.emilia-romagna.it/
__ http://www.ausl.fe.it/
__ http://www.comune.modena.it/
__ http://www.plonegov.it/

Authors
=======

This product was developed by RedTurtle Technology team.

.. image:: http://www.redturtle.net/redturtle_banner.png
   :alt: RedTurtle Technology Site
   :target: http://www.redturtle.net/

Thanks to:

* *Mauro Amico* (mamico) for providing support and fixing issues.
* *Stefan Strasser* for testing the product on Plone 4, and reports problems

Before this: ComboLink
----------------------

Part of the code of Smart Link was taken from the `ComboLink`__ Plone (and Plonegov) product.
This project was giving the same internal link feature in old 2.1/2.5 Plone releases.

__ http://plone.org/products/combolink/

