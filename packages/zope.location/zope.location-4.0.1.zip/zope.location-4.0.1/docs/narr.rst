Using :mod:`zope.location`
==========================

:class:`~zope.location.location.Location`
-----------------------------------------

The `Location` base class is a mix-in that defines `__parent__` and
`__name__` attributes.

Usage within an Object field:

.. doctest::

  >>> from zope.interface import implementer, Interface
  >>> from zope.schema import Object
  >>> from zope.schema.fieldproperty import FieldProperty
  >>> from zope.location.interfaces import ILocation
  >>> from zope.location.location import Location
  
  >>> class IA(Interface):
  ...     location = Object(schema=ILocation, required=False, default=None)
  >>> @implementer(IA)
  ... class A(object):
  ...     location = FieldProperty(IA['location'])
  
  >>> a = A()
  >>> a.location = Location()
  
  >>> loc = Location(); loc.__name__ = u'foo'
  >>> a.location = loc
  
  >>> loc = Location(); loc.__name__ = None
  >>> a.location = loc
  
  >>> loc = Location(); loc.__name__ = 'foo'
  >>> a.location = loc
  Traceback (most recent call last):
  ...
  WrongContainedType: ([WrongType('foo', <type 'unicode'>, '__name__')], 'location')


:func:`~zope.location.location.inside`
--------------------------------------

The `inside` function tells if l1 is inside l2.  L1 is inside l2 if l2 is an
ancestor of l1.

.. doctest::

  >>> o1 = Location()
  >>> o2 = Location(); o2.__parent__ = o1
  >>> o3 = Location(); o3.__parent__ = o2
  >>> o4 = Location(); o4.__parent__ = o3
  
  >>> from zope.location.location import inside

  >>> inside(o1, o1)
  True

  >>> inside(o2, o1)
  True

  >>> inside(o3, o1)
  True

  >>> inside(o4, o1)
  True
  
  >>> inside(o1, o4)
  False
  
  >>> inside(o1, None)
  False


:class:`~zope.location.location.LocationProxy`
----------------------------------------------

`LocationProxy` is a non-picklable proxy that can be put around
objects that don't implement `ILocation`.

.. doctest::

  >>> from zope.location.location import LocationProxy
  >>> l = [1, 2, 3]
  >>> ILocation.providedBy(l)
  False
  >>> p = LocationProxy(l, "Dad", "p")
  >>> p
  [1, 2, 3]
  >>> ILocation.providedBy(p)
  True
  >>> p.__parent__
  'Dad'
  >>> p.__name__
  'p'
  
  >>> import pickle
  >>> p2 = pickle.dumps(p)
  Traceback (most recent call last):
  ...
  TypeError: Not picklable

Proxies should get their doc strings from the object they proxy:

.. doctest::

  >>> p.__doc__ == l.__doc__
  True

If we get a "located class" somehow, its doc string well be available
through proxy as well:

.. doctest::

  >>> class LocalClass(object):
  ...     """This is class that can be located"""

  >>> p = LocationProxy(LocalClass)
  >>> p.__doc__ == LocalClass.__doc__
  True

:func:`~zope.location.location.LocationInterator`
-------------------------------------------------

This function allows us to iterate over object and all its parents.

.. doctest::

  >>> from zope.location.location import LocationIterator

  >>> o1 = Location()
  >>> o2 = Location()
  >>> o3 = Location()
  >>> o3.__parent__ = o2
  >>> o2.__parent__ = o1

  >>> iter = LocationIterator(o3)
  >>> iter.next() is o3
  True
  >>> iter.next() is o2
  True
  >>> iter.next() is o1
  True
  >>> iter.next()
  Traceback (most recent call last):
  ...
  StopIteration


:func:`~zope.location.location.located`
---------------------------------------

`located` locates an object in another and returns it:

.. doctest::

  >>> from zope.location.location import located
  >>> a = Location()
  >>> parent = Location()
  >>> a_located = located(a, parent, 'a')
  >>> a_located is a
  True
  >>> a_located.__parent__ is parent
  True
  >>> a_located.__name__
  'a'

If we locate the object again, nothing special happens:

.. doctest::

  >>> a_located_2 = located(a_located, parent, 'a')
  >>> a_located_2 is a_located
  True

If the object does not provide ILocation an adapter can be provided:

.. doctest::

  >>> import zope.interface
  >>> import zope.component
  >>> sm = zope.component.getGlobalSiteManager()
  >>> sm.registerAdapter(LocationProxy, required=(zope.interface.Interface,))
  
  >>> l = [1, 2, 3]
  >>> parent = Location()
  >>> l_located = located(l, parent, 'l')
  >>> l_located.__parent__ is parent
  True
  >>> l_located.__name__
  'l'
  >>> l_located is l
  False
  >>> type(l_located)
  <class 'zope.location.location.LocationProxy'>
  >>> l_located_2 = located(l_located, parent, 'l')
  >>> l_located_2 is l_located
  True

When changing the name, we still do not get a different proxied object:

.. doctest::

  >>> l_located_3 = located(l_located, parent, 'new-name')
  >>> l_located_3 is l_located_2
  True

  >>> sm.unregisterAdapter(LocationProxy, required=(zope.interface.Interface,))
  True
