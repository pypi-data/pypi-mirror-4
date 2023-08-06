=====================
Additional Namespaces
=====================

Principal
---------

The ``principal`` namespace allows to differentiate between usernames
in the url. This is usefull for caching on a per principal basis. The
namespace itself doesn't change anything. It just checks if the
principal is the one that is logged in.

    >>> from z3c.traverser import namespace
    >>> from zope.publisher.browser import TestRequest
    >>> class Request(TestRequest):
    ...     principal = None
    ...
    ...     def shiftNameToApplication(self):
    ...         pass

    >>> class Principal(object):
    ...     def __init__(self, id):
    ...         self.id = id

    >>> pid = 'something'
    >>> r = Request()
    >>> r.principal = Principal('anonymous')

If we have the wrong principal we get an Unauthorized exception.

    >>> ns = namespace.principal(object(), r)
    >>> ns.traverse('another', None) # doctest: +IGNORE_EXCEPTION_DETAIL
    Traceback (most recent call last):
    ...
    Unauthorized: ++principal++another

Otherwise not

    >>> ns.traverse('anonymous', None)
    <object object at ...>
