====================
 Viewlet Traversing
====================

Traversing to viewlets is done via namespaces.

  >>> from webtest.app import TestApp
  >>> browser = TestApp(wsgi_app)
  >>> res = browser.get('http://localhost/@@test.html')

We have a test page registered that contains our viewlet. The viewlet
itself just renders a link to its location (this is just for testing).

  >>> print(res.html)
  <html>
    <body>
       <div><div><a
       href="http://localhost/test.html/++manager++IMyManager/++viewlet++MyViewlet">My
       Viewlet</a></div></div>
    </body>
  </html>

Let's follow the link to traverse the viewlet directly.

  >>> res = res.click('My Viewlet')
  >>> res.request.url
  'http://localhost/test.html/++manager++IMyManager/++viewlet++MyViewlet'
  >>> print(res.body.decode())
  <div><a href="http://localhost/test.html/++manager++IMyManager/++viewlet++MyViewlet">My Viewlet</a></div>

What happens if a viewlet managers is nested into another viewlet? To test
this we will create another manager and another viewlet::

  >>> res = browser.get('http://localhost/@@nested.html')
  >>> print(res.html)
  <html>
    <body>
      <div><div><a href="http://localhost/nested.html/++manager++IOuterManager/++viewlet++OuterViewlet/++manager++IInnerManager/++viewlet++InnerViewlet/++manager++IMostInnerManager/++viewlet++MostInnerViewlet">Most inner viewlet</a></div></div>
    </body>
  </html>

Let's follow the link to traverse the viewlet directly.

  >>> res = res.click('Most inner viewlet')
  >>> res.request.url
  'http://localhost/nested.html/++manager++IOuterManager/++viewlet++OuterViewlet/++manager++IInnerManager/++viewlet++InnerViewlet/++manager++IMostInnerManager/++viewlet++MostInnerViewlet'

  >>> print(res.body.decode())
  <div><a href="http://localhost/nested.html/++manager++IOuterManager/++viewlet++OuterViewlet/++manager++IInnerManager/++viewlet++InnerViewlet/++manager++IMostInnerManager/++viewlet++MostInnerViewlet">Most inner viewlet</a></div>


Caveats
-------

Update of the manager is not called, because this may be too expensive
and normally the managers update just collects viewlets.
