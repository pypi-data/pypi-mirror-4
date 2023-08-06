========
Glossary
========

.. glossary::

   controller
   controller callable
      A callable that accepts a :py:class:`~milla.Request` instance and any
      optional parameters and returns a response

   permission requirement
      A set of permissions required to access a particular URL path. Permission
      requirements are specified by using the
      :py:meth:`~milla.auth.require_perm` decorator on a restricted
      :term:`controller callable`

   request validator
      A function that checks a request to ensure it meets the specified
      :term:`permission requirement` before calling a :term:`controller
      callable`

   root object
      The starting object in the object traversal URL dispatch mechanism from
      which all path lookups are performed

   URL dispatcher
      An object that maps request paths to :term:`controller` callables
