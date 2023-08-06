===============================================
Extracting Information from the Traversal Stack
===============================================

This package allows to define virtual traversal paths for collecting
arbitrary information from the traversal stack instead of, for
example, query strings.

In contrast to the common way of defining custom Traversers, this
implementation does not require to go through the whole traversal
process step by step. The traversal information needed is taken from
the traversalstack directly and the used parts of the stack are
consumed. This way one don't have to define proxy classes just for
traversal.

This implementation does not work in tales because it requires the
traversalstack of the request.

For each name in the traversal stack a named multiadapter is looked up
for ITraversalStackConsumer, if found the item gets removed from the
stack and the adapter is added to the request annotation.

  >>> from z3c.traverser.stackinfo import traversing
  >>> from z3c.traverser.stackinfo import interfaces

If there are no adapters defined, the traversalstack is kept as is. To
show this behaviour we define some sample classes.

  >>> from zope import interface
  >>> class IContent(interface.Interface):
  ...     pass

  >>> from zope.site.folder import Folder
  >>> @interface.implementer(IContent)
  ... class Content(Folder):
  ...     pass

There is a convinience function which returns an iterator which
iterates over tuples of adapterName, adapter. Additionally the
traversal stack of the request is consumed if needed.

  >>> from zope.publisher.browser import TestRequest
  >>> from zope.publisher.interfaces.browser import IBrowserRequest
  >>> request = TestRequest()

We set the traversal stack manually for testing here.

  >>> request.setTraversalStack([u'index.html', u'path', u'some'])
  >>> content = Content()

So if no ITraversalStackConsumer adapters are found the stack is left
untouched.

  >>> list(traversing.getStackConsumers(content, request))
  []
  >>> request.getTraversalStack()
  [u'index.html', u'path', u'some']

There is a base class for consumer implementations which implements
the ITraversalStackConsumer interface.

  >>> from z3c.traverser.stackinfo import consumer
  >>> from zope.interface.verify import verifyObject
  >>> o = consumer.BaseConsumer(None, None)
  >>> verifyObject(interfaces.ITraversalStackConsumer,o)
  True

Let us define a custom consumer.

  >>> from zope import component
  >>> class DummyConsumer(consumer.BaseConsumer):
  ...     component.adapts(IContent, IBrowserRequest)
  >>> component.provideAdapter(DummyConsumer, name='some')

Now we will find the newly registered consumer and the 'some' part of
the stack is consumed.

  >>> consumers = list(traversing.getStackConsumers(content, request))
  >>> consumers
  [(u'some', <DummyConsumer named u'some'>)]
  >>> request.getTraversalStack()
  [u'index.html', u'path']

Each consumer at least has to consume one element, which is always
the name under which the adapter was registered under.

  >>> name, cons = consumers[0]
  >>> cons.__name__
  u'some'

Let us provide another adapter, to demonstrate that the adpaters
always have the reverse order of the traversal stack. This is actually
the order in the url.

  >>> component.provideAdapter(DummyConsumer, name='other')
  >>> stack = [u'index.html', u'path', u'some', u'other']
  >>> request.setTraversalStack(stack)
  >>> consumers = list(traversing.getStackConsumers(content, request))
  >>> consumers
  [(u'other', <DummyConsumer named u'other'>),
   (u'some', <DummyConsumer named u'some'>)]

  >>> [c.__name__ for name, c in consumers]
  [u'other', u'some']

The arguments attribute of the consumer class defines how many
arguments are consumed/needed from the stack. Let us create a KeyValue
consumer, that should extract key value pairs from the stack.

  >>> class KeyValueConsumer(DummyConsumer):
  ...     arguments=('key', 'value')
  >>> component.provideAdapter(KeyValueConsumer, name='kv')
  >>> stack = [u'index.html', u'value', u'key', u'kv']
  >>> request.setTraversalStack(stack)
  >>> consumers = list(traversing.getStackConsumers(content, request))
  >>> consumers
  [(u'kv', <KeyValueConsumer named u'kv'>)]
  >>> request.getTraversalStack()
  [u'index.html']
  >>> name, cons = consumers[0]
  >>> cons.key
  u'key'
  >>> cons.value
  u'value'

We can of course use multiple consumers of the same type.

  >>> stack = [u'index.html', u'v2', u'k2', u'kv', u'v1', u'k1', u'kv']
  >>> request.setTraversalStack(stack)
  >>> consumers = list(traversing.getStackConsumers(content, request))
  >>> [(c.__name__, c.key, c.value) for name, c in consumers]
  [(u'kv', u'k1', u'v1'), (u'kv', u'k2', u'v2')]

If we have too less arguments a NotFound exception.

  >>> stack = [u'k2', u'kv', u'v1', u'k1', u'kv']
  >>> request.setTraversalStack(stack)
  >>> consumers = list(traversing.getStackConsumers(content, request))
  Traceback (most recent call last):
    ...
  NotFound: Object: <Content object at ...>, name: u'kv'


In order to actually use the stack consumers to retrieve information,
there is another convinience function which stores the consumers in
the requests annotations. This should noramlly be called on
BeforeTraverseEvents.

  >>> stack = [u'index.html', u'v2', u'k2', u'kv', u'v1', u'k1', u'kv']
  >>> request.setTraversalStack(stack)
  >>> traversing.applyStackConsumers(content, request)
  >>> request.annotations[traversing.CONSUMERS_ANNOTATION_KEY]
  [<KeyValueConsumer named u'kv'>,
   <KeyValueConsumer named u'kv'>]

Instead of messing with the annotations one just can adapt the request
to ITraversalStackInfo.

  >>> component.provideAdapter(consumer.requestTraversalStackInfo)
  >>> ti = interfaces.ITraversalStackInfo(request)
  >>> ti
  (<KeyValueConsumer named u'kv'>, <KeyValueConsumer named u'kv'>)

  >>> len(ti)
  2

The adapter always returs an empty TraversalStackInfoObject if there
is no traversalstack information.

  >>> request = TestRequest()
  >>> ti = interfaces.ITraversalStackInfo(request)
  >>> len(ti)
  0


Virtual Host
------------

If virtual hosts are used the traversal stack contains aditional information
for the virtual host which will interfere which the stack consumer.

  >>> stack = [u'index.html', u'value', u'key',
  ...          u'kv', u'++', u'inside vh', '++vh++something']
  >>> request.setTraversalStack(stack)
  >>> consumers = list(traversing.getStackConsumers(content, request))
  >>> consumers
  [(u'kv', <KeyValueConsumer named u'kv'>)]
  >>> request.getTraversalStack()
  [u'index.html', u'++', u'inside vh', '++vh++something']


URL Handling
------------

Let us try these things with a real url, in our test the root is the site.

  >>> from zope.traversing.browser.absoluteurl import absoluteURL
  >>> absoluteURL(root, request)
  'http://127.0.0.1'

There is an unconsumedURL function which returns the url of an object
with the traversal information, which is normally omitted.

  >>> request = TestRequest()
  >>> root['content'] = content
  >>> absoluteURL(root['content'], request)
  'http://127.0.0.1/content'
  >>> stack = [u'index.html', u'v2 space', u'k2', u'kv', u'v1', u'k1', u'kv']
  >>> request.setTraversalStack(stack)
  >>> traversing.applyStackConsumers(root['content'], request)
  >>> traversing.unconsumedURL(root['content'], request)
  'http://127.0.0.1/content/kv/k1/v1/kv/k2/v2%20space'

Let us have more than one content object

  >>> under = content[u'under'] = Content()
  >>> request = TestRequest()
  >>> traversing.unconsumedURL(under, request)
  'http://127.0.0.1/content/under'

We add some consumers to the above object

  >>> request = TestRequest()
  >>> stack = [u'index.html', u'value1', u'key1', u'kv']
  >>> request.setTraversalStack(stack)
  >>> traversing.applyStackConsumers(root['content'], request)
  >>> traversing.unconsumedURL(root['content'], request)
  'http://127.0.0.1/content/kv/key1/value1'
  >>> traversing.unconsumedURL(under, request)
  'http://127.0.0.1/content/kv/key1/value1/under'

And now to the object below too.

  >>> request = TestRequest()
  >>> stack = [u'index.html', u'value1', u'key1', u'kv']
  >>> request.setTraversalStack(stack)
  >>> traversing.applyStackConsumers(root['content'], request)
  >>> stack = [u'index.html', u'value2', u'key2', u'kv']
  >>> request.setTraversalStack(stack)
  >>> traversing.applyStackConsumers(under, request)
  >>> traversing.unconsumedURL(root['content'], request)
  'http://127.0.0.1/content/kv/key1/value1'
  >>> traversing.unconsumedURL(under, request)
  'http://127.0.0.1/content/kv/key1/value1/under/kv/key2/value2'

Or only the object below.

  >>> request = TestRequest()
  >>> traversing.applyStackConsumers(root['content'], request)
  >>> stack = [u'index.html', u'value2', u'key2', u'kv']
  >>> request.setTraversalStack(stack)
  >>> traversing.applyStackConsumers(under, request)
  >>> traversing.unconsumedURL(root['content'], request)
  'http://127.0.0.1/content'
  >>> traversing.unconsumedURL(under, request)
  'http://127.0.0.1/content/under/kv/key2/value2'

The unconsumedURL function is also available as a view, named
``unconsumed_url``, similar to ``absolute_url`` one.

  >>> from zope.component import getMultiAdapter
  >>> url = getMultiAdapter((under, request), name='unconsumed_url')

  >>> str(url)
  'http://127.0.0.1/content/under/kv/key2/value2'

  >>> url()
  'http://127.0.0.1/content/under/kv/key2/value2'
