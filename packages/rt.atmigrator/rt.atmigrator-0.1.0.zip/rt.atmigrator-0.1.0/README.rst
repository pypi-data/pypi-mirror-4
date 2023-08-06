Introduction
============
This simple package allows to migrate from a portal-type to another.
This is done by `Products.contentmigration <https://pypi.python.org/pypi/Products.contentmigration>`_, we only provide a simple interface that allows to select source and destination portal_types.

Installation
============
You only need to add the product to eggs and launch the buildout. No installation needed, is only a view.

buildout.cfg::

    [instance]
    eggs +=
         rt.atmigrator

Usage
=====
To migrate some contents, you only need to call "*@@migrate-types*" view in site root.

Remember to update the catalog after migration to align metadatas.

.. image:: http://blog.redturtle.it/pypi-images/rt.atmigrator/atmigrator_screenshot.png

TODO
====
* Handle more specific queries (for example filtering by path or review_state)
* Handle custom migration behaviors (pre and post migration) for specified portal_types with some additional plugins

Compatibility
=============
This product is tested with Plone 3.3.x and 4.2.x (with tests).

Authors
=======

This product was developed by RedTurtle Technology team.

.. image:: http://www.redturtle.net/redturtle_banner.png
   :alt: RedTurtle Technology Site
   :target: http://www.redturtle.net/

