===================
Traversing Viewlets
===================

This package allows to traverse viewlets and viewletmanagers. It also
provides absolute url views for those objects which are described in
this file, for traversers see BROWSER.txt.

  >>> from z3c.traverser.viewlet import browser

Let us define some test classes.

  >>> import zope.component
  >>> from zope.viewlet import manager
  >>> from zope.viewlet import interfaces
  >>> from zope.publisher.interfaces.browser import IDefaultBrowserLayer
  >>> import zope.interface
  >>> class ILeftColumn(interfaces.IViewletManager):
  ...     """Viewlet manager located in the left column."""
  >>> LeftColumn = manager.ViewletManager('left', ILeftColumn)
  >>> zope.component.provideAdapter(
  ...     LeftColumn,
  ...     (zope.interface.Interface,
  ...     IDefaultBrowserLayer, zope.interface.Interface),
  ...     interfaces.IViewletManager, name='left')

You can then create a viewlet manager using this interface now:


  >>> from zope.viewlet import viewlet
  >>> from zope.container.contained import Contained

  >>> class Content(Contained):
  ...     pass
  >>> root['content'] = Content()
  >>> content = root['content']
  >>> from zope.publisher.browser import TestRequest
  >>> request = TestRequest()
  >>> from zope.publisher.interfaces.browser import IBrowserView
  >>> from zope.publisher.browser import BrowserView
  >>> class View(BrowserView):
  ...     pass

We have to set the name, this is normally done in zcml.

  >>> view = View(content, request)
  >>> view.__name__ = 'test.html'
  >>> leftColumn = LeftColumn(content, request, view)

Let us create a simple viewlet. Note that we need a __name__ attribute
in order to make the viewlet traversable. Normally you don't have to
take care of this, because the zcml directive sets the name upon
registration.

  >>> class MyViewlet(viewlet.ViewletBase):
  ...     __name__ = 'myViewlet'
  ...     def render(self):
  ...         return u'<div>My Viewlet</div>'
  >>> from zope.security.checker import NamesChecker, defineChecker
  >>> viewletChecker = NamesChecker(('update', 'render'))
  >>> defineChecker(MyViewlet, viewletChecker)

  >>> zope.component.provideAdapter(
  ...     MyViewlet,
  ...     (zope.interface.Interface, IDefaultBrowserLayer,
  ...     IBrowserView, ILeftColumn),
  ...     interfaces.IViewlet, name='myViewlet')

We should now be able to get the absolute url of the viewlet and the
manager. We have to register the adapter for the test.

  >>> from zope.traversing.browser.interfaces import IAbsoluteURL
  >>> from zope.traversing.browser import absoluteurl

  >>> zope.component.provideAdapter(
  ...     browser.ViewletAbsoluteURL,
  ...     (interfaces.IViewlet, IDefaultBrowserLayer),
  ...     IAbsoluteURL)
  >>> zope.component.provideAdapter(
  ...     browser.ViewletManagerAbsoluteURL,
  ...     (interfaces.IViewletManager, IDefaultBrowserLayer),
  ...     IAbsoluteURL, name="absolute_url")
  >>> zope.component.provideAdapter(
  ...     browser.ViewletManagerAbsoluteURL,
  ...     (interfaces.IViewletManager, IDefaultBrowserLayer),
  ...     IAbsoluteURL)
  >>> myViewlet = MyViewlet(content, request, view, leftColumn)
  >>> absoluteurl.absoluteURL(leftColumn, request)
  'http://127.0.0.1/content/test.html/++manager++left'
  >>> absoluteurl.absoluteURL(myViewlet, request)
  '.../content/test.html/++manager++left/++viewlet++myViewlet'

