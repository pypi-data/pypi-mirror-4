==========
Change Log
==========


0.2
===

* Python 3 support
* Added new utility functions:

  * :py:func:`~milla.util.http_date`
  * :py:func:`~milla.util.read_config`

* Added :py:meth:`~milla.Request.static_resource`
* Corrected default handling of HTTP ``OPTIONS`` requests (`Issue #5`_)
* Deprecated :py:mod:`milla.cli`
* Deprecated :py:class:`~milla.dispatch.routing.Generator` in favor of
  :py:meth:`~milla.Request.create_href`

0.1.2
=====

* Improvements to :py:class:`~milla.controllers.FaviconController` (`Issue
  #1`_)

0.1.1
=====

* Fixed a bug when generating application-relative URLs with
  :py:class:`~milla.routing.dispatch.URLGenerator`:

0.1
===

Initial release

.. _Issue #1: https://bitbucket.org/AdmiralNemo/milla/issue/1
.. _Issue #5: https://bitbucket.org/AdmiralNemo/milla/issue/5
