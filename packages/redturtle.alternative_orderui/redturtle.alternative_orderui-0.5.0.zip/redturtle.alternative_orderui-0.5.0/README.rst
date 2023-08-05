Introduction
============

An alternative *folder_contents* forms, that disable someway KSS ordering and show another fast way
to reorder items (less and less cool, but this is working most of the time).

The new UI is not using fantastic AJAX/KSS technology, but reload the whole page, simply using basic
features that you always have when Javascript is disabled in your browser.

So... use this only when you (or your users) experience some problem with KSS ordering
(not always this happens, but happens...). If no-one report a problem with the basic Plone drag&drop
sort mechanism, you don't need this product.

Assumptions made in themes
--------------------------

The script try to be smart as possible, being general and not based to Plone UI and theme installed.

* It choose the sorting cell looking for "*draggable*" CSS class
* It choose the checkbox cell looking for "*notDraggable*" CSS class
* The cell where to take the title of the document (used when prompt user) must be the one after
  the "*notDraggable*"

TODO
====

* Use jQuery Tools features if installed instead of the ugly Javascript confirm
* Find a KSS way to disable KSS

Credits
=======

Developed with the support of:

* `Azienda USL Ferrara`__
  
  .. image:: http://www.ausl.fe.it/logo_ausl.gif
     :alt: Azienda USL's logo
  
* `Regione Emilia Romagna`__

All of them supports the `PloneGov initiative`__.

__ http://www.ausl.fe.it/
__ http://www.regione.emilia-romagna.it/
__ http://www.plonegov.it/

Authors
=======

This product was developed by RedTurtle Technology team.

.. image:: http://www.redturtle.net/redturtle_banner.png
   :alt: RedTurtle Technology Site
   :target: http://www.redturtle.net/

