================
EdW User History
================

Introduction
============

`EdW User History`_ package will make available a portlet providing user login history.
The portlet will list the most recent 10 user logins. Clicking a userid will open a
page showing the full login history for that user including login date and his/her IP.
A full user listing page is also available in the "Site setup" section of the site.

Main features
=============

1. New available portlet called "User login history"
2. Control panel tool to display the full login history
3. Login history works not only for local users but for external user sources too

Installation
============

zc.buildout
~~~~~~~~~~~
If you are using `zc.buildout`_ and the `plone.recipe.zope2instance`_
recipe to manage your project, you can do this:

* Update your buildout.cfg file:

  * Add ``edw.userhistory`` to the list of eggs to install
  * Tell the plone.recipe.zope2instance recipe to install a ZCML slug

  ::

    [instance]
    ...
    eggs =
      ...
      edw.userhistory

    zcml =
      ...
      edw.userhistory

* Re-run buildout, e.g. with::

  $ ./bin/buildout

You can skip the ZCML slug if you are going to explicitly include the package
from another package's configure.zcml file.

Copyright and license
=====================

The Initial Owner of the Original Code is Eau de Wed (EdW).
All Rights Reserved.

The EdW User History (the Original Code) is free software;
you can redistribute it and/or modify it under the terms of the GNU
General Public License as published by the Free Software Foundation;
either version 2 of the License, or (at your option) any later
version.

More details under edw.userhistory/docs/License.txt

.. _`EdW User History`: https://github.com/collective/edw.userhistory
.. _`plone.recipe.zope2instance`: http://pypi.python.org/pypi/plone.recipe.zope2instance