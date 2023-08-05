.. contents::

Introduction
============

``plomino.patternslib`` is a Plomino_ plugin that provides fields and other form elements built using the 
`Patternslib`_  javascript library.  In its initial implementation, the *Chosen* select boxes from *HarvestHQ* are 
made available.

For more information, see the `Related Links`_ below.

Installation
============
Add ``plomino.patternslib`` to the list of ``eggs`` of your ``plone.recipe.zope2instance`` section.  Re-run buildout.

Use
===
Activate ``plomino.patternslib`` either in ``portal_quickinstaller``, or from the ``/prefs_install_products_form`` 
Add-ons control panel on your Plone site.

Assuming you already have Plomino installed on your site, you will now have a new field type **Chosen** available to add
to your Plomino forms. It can be configured exactly like a *Selection List* field.

Examples
========
To see working examples of the style and behavior of the **Chosen** field, see Harvest_.  Currently, only the 
*Multiple Select* type is available, but more will be added in upcoming releases.

Related Links
=============
.. target-notes::
.. _Plomino: http://plomino.net
.. _Patternslib: http://patternslib.com/
.. _Harvest: http://harvesthq.github.com/chosen/
