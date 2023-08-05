Introduction
============

This product is only useful if you are in the very sad situation of needing a Plone product on a Plone 3.3
installation, but the product is now compatible only with Plone 4+.

Keeping code compatibility with older version is commonly simple (see "`Upgrading Plone 3.x to 4.0`__" and
"`Upgrading Plone 4.0 to 4.1`__").

__ http://plone.org/documentation/manual/upgrade-guide/version/upgrading-plone-3-x-to-4.0 
__ http://plone.org/documentation/manual/upgrade-guide/version/upgrading-plone-4.0-to-4.1/referencemanual-all-pages

However there's a major problem: **Generic Setup import step changes**.
Sadly those changes are difficult to be backported (because no-one wants to maintain a Plone-3-only compatible
profile).

How it works
============

This product will **not** backport Generic Setup new features to Plone 4.3, but monkey-patch Generic Setup to
*tolerate* new XML parameters.

cssregistry
-----------

Old **CSSRegistry** registration didn't know nothing about ``authenticated``, ``applyPrefix`` and ``bundle``
paramenters.

Those parameters are now ignored.

If ``authenticated`` is provided and ``expression`` is not provided, the new ``authenticated`` feature is
translated in the old way (using ``expression``).

jsregistry
----------

Old **CSSRegistry** registration didn't know nothing about ``authenticated``, and ``bundle`` paramenters.

Those parameters are now ignored.

If ``authenticated`` is provided and ``expression`` is not provided, the new ``authenticated`` feature is
translated in the old way (using ``expression``).

types
-----

Old **PropertyManagerHelpers** supports only ``content_icon`` registration instead of the new ``icon_expr``.

If ``icon_expr`` is provided, it will be used as ``content_icon``. Also: an attempt to fix the data format is done.

Authors
=======

This product was developed by RedTurtle Technology team.

.. image:: http://www.redturtle.it/redturtle_banner.png
   :alt: RedTurtle Technology Site
   :target: http://www.redturtle.it/
