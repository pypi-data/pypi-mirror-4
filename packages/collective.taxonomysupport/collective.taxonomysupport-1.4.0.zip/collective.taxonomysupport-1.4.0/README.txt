.. contents:: **Table of contents**

What is this?
=============

This product add a new field to all Plone contents (someway similar to the keyword field) that allow to
select one or more **taxonomies** to reference.

A Taxonomy is commonly like normal folder and you can create them all around the site. They gives only some
differences when you add additional contents inside them (but to select a taxonomy for a content
you don't need that the content is inside it).

Also the *taxonomy support* must be explicitly enabled on the site root and/or in one or many of the
site's subsections.
In this way you can have different taxonomies set in different areas of the site.

The list of taxonomies selectable on simple contents is filtered locally if there are different sections activated.

The activation to one section block the inheritance of other taxonomies from upper levels.

Filtering policies are the following:

* if there isn't any parent of the object that implements the "*ITaxonomyLevel*" interface, no
  taxonomy will be shown and so no one are selectable.
* if there are one or more parents that provides the interface, we take the nearest parent and search
  its availables taxonomies.
* if there aren't taxonomies, or there isn't any activated object (object that implements ITaxonomyLevel
  interface; it could be also the site root) the field doesn't appears in the field edit form.
* if an object is created inside a taxonomy, the taxonomy will be the default value in the field.

How to use?
===========

To activate the taxonomy level you can access the "*Add to taxonomy roots*" in the "Action" menu.

Create Taxonomy folders normally in the site.

You can also mark any other object as a *Taxonomy-like* but to do this you need to manually apply the
``collective.taxonomysupport.interfaces.IFolderTaxonomy`` interface.

Collection criteria
-------------------

This product add also a new collection criteria (*Site Areas*) for easilly use taxonomies in (old-style) collections.


Updating the catalog
====================
Taxonomies stores 2 indexes in catalog: **getSiteAreas** and **SiteAreas**.

The first index stores a list of uids fo selected taxonomies of an object, and the second (SiteAreas) stores the titles of selected taxonomies, for a human-usage.
If you need to update the all catalog (or even rebuild it), "SiteAreas" indexes and metadata will be partially inconsistent because the indexer method make a catalog query to get the taxonomy right titles, so you need to do 2 more steps:

* reindex "SiteAreas" index from portal_catalog in ZMI
* launch a view that update metadatas for all items in the catalog with a selected taxonomy: http://your-plone-site/@@fix-metadata


Dependencies
============

This product has been tested on:

* Plone 3.3
* Plone 4.2


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
