===============================================
Extracting Information from the Traversal Stack
===============================================

This is a simple example to demonstrate the usage of this
package. Please take a look into the testing directory to see how
things should be set up.

  >>> from webtest.app import TestApp
  >>> browser = TestApp(wsgi_app,
  ...     extra_environ={'wsgi.handleErrors': False,
  ...                    'paste.throw_errors': True,
  ...                    'x-wsgiorg.throw_errors': True})
  >>> res = browser.get('http://localhost/@@stackinfo.html')

So basically we have no stack info.

  >>> print(res.body.decode())
  Stack Info from object at http://localhost/stackinfo.html:

Let us try to set foo to bar.

  >>> res = browser.get('http://localhost/kv/foo/bar/@@stackinfo.html')
  >>> print(res.body.decode())
  Stack Info from object at http://localhost/stackinfo.html:
  consumer kv:
  key = u'foo'
  value = u'bar'

Two consumers.

  >>> res = browser.get(
  ...     'http://localhost/kv/foo/bar/kv/time/late/@@stackinfo.html')
  >>> print(res.body.decode())
  Stack Info from object at http://localhost/stackinfo.html:
  consumer kv:
  key = u'foo'
  value = u'bar'
  consumer kv:
  key = u'time'
  value = u'late'

Invalid url:

  >>> browser.get('http://localhost/kv/foo/bar/kv/@@stackinfo.html') \
  ...     # doctes: +IGNORE_EXCEPTION_DETAIL
  Traceback (most recent call last):
  ...
  NotFound: Object: <...Folder object at ...>, name: u'kv'


