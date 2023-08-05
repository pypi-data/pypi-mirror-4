************
ZODB Recipes
************

Recipes for working with ZODB.

.. contents::

Changes
*******

0.6.2 (2012-10-31)
==================

Bugs Fixed
----------

- Moved 'zope.testing' requirement from install to test requirement.

0.6.1 (2010-05-25)
==================

Bugs Fixed
----------

- Pack scripts were incorrectly generated for storages that weren't
  named in their storage configurations.

0.6.0 (2009-12-03)
==================

New Features
------------

- Generation of a logrotate configuration can now be disabled by
  providing a logrotate option with a value of "false".

- Added documentation of the eggs option and why it generally
  shouldn't be used.

- Improved error handling.

Bugs Fixed
----------

- The eggs option, when used, wasn't handled properly.


0.5.0 (2008-11-03)
==================

New Features
------------

You can now specify a name option in server parts to have installed
files use a different name than the section name.

Bugs Fixed
----------

Pack crontab files weren't removed when parts were removed or renamed.

0.4 (2008-02-18)
================

New Features
------------

The server recipe now honors the deployment name option.

0.3.1 (2008-01-03)
==================

Bugs Fixed
----------

Shell-scripts using su weren't generated correctly.

0.3 (2008-01-03)
================

New Features
------------

- You can now specify an email address in a packing crontab file to
  control where errors are sent.

- If you install a general ZEO script, using a zdaemon part::

    [zdaemon]
    recipe = zc.recipe.egg:script
    eggs = zdaemon

  you can request that shell scripts be generated that use the generic
  zdaemon script. This can make updating software for deployed systems
  easier since instance-specific scripts don't depend on paths, like
  egg names, that are likely to change.

Bugs Fixed
----------

- ZODB3 and most of its requirements were spurious dependencies of the
  recipes. This caused ZODB3 to be installed using the Python used to
  run the buildout, which caused problems in some circumstances.

0.2.1 (2007-04-23)
==================

Bugs Fixed
----------

- crontab and logrotate configuration files were being generates incorrectly.

0.2 (2007-04-17)
================

Added handling of %import directives.

0.1 (2007-04-13)
================

Initial release.
