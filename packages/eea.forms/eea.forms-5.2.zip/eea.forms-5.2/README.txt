=========
EEA Forms
=========
.. image:: http://ci.eionet.europa.eu/job/eea.forms-www/badge/icon
  :target: http://ci.eionet.europa.eu/job/eea.forms-www/lastBuild
.. image:: http://ci.eionet.europa.eu/job/eea.forms-plone4/badge/icon
  :target: http://ci.eionet.europa.eu/job/eea.forms-plone4/lastBuild

Introduction
============

This package is a collection of custom AT Widgets and Fields:
  - Quick Upload Widget based on collective.quickupload
  - Management Plan Widget/Field
It also provides some custom jQuery plugins:
  - EEAFormsGroup -- group AT Widgets within an accordion in edit form
  - EEAFormsWizard -- make schemata tabs a wizard like form with back and
                      forward buttons
  - EEAFormsQuickUpload -- collective.quickupload jQuery plugin to be used with
    QuickUpload Widget.

.. note ::

  This add-on doesn't do anything by itself. It needs to be integrated by a
  developer within your own products. For reference you can check
  the `eea.daviz`_ package.


.. contents::


Installation
============

zc.buildout
-----------
If you are using `zc.buildout`_ and the `plone.recipe.zope2instance`_
recipe to manage your project, you can do this:

* Update your buildout.cfg file:

  * Add ``eea.forms`` to the list of eggs to install
  * Tell the `plone.recipe.zope2instance`_ recipe to install a ZCML slug

  ::

    [instance]
    ...
    eggs =
      ...
      eea.forms

    zcml =
      ...
      eea.forms

* Re-run buildout, e.g. with::

  $ ./bin/buildout

You can skip the ZCML slug if you are going to explicitly include the package
from another package's configure.zcml file.

* Install eea.forms within Site Setup > Add-ons


Dependencies
============

`EEA Forms`_ has the following dependencies:
  - Plone 4+
  - collective.quickupload


Source code
===========

Latest source code (Plone 4 compatible):
  - `Plone Collective on Github <https://github.com/collective/eea.forms>`_
  - `EEA on Github <https://github.com/eea/eea.forms>`_


Copyright and license
=====================
The Initial Owner of the Original Code is European Environment Agency (EEA).
All Rights Reserved.

The eea.forms (the Original Code) is free software;
you can redistribute it and/or modify it under the terms of the GNU
General Public License as published by the Free Software Foundation;
either version 2 of the License, or (at your option) any later
version.

More details under docs/License.txt


Funding
=======

  EEA_ - European Environment Agency (EU)

.. _EEA: http://www.eea.europa.eu/
.. _`eea.daviz`: http://eea.github.com/docs/eea.daviz
.. _`plone.recipe.zope2instance`: http://pypi.python.org/pypi/plone.recipe.zope2instance
.. _`zc.buildout`: http://pypi.python.org/pypi/zc.buildout
