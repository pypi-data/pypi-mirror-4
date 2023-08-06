:mod:`zope.location` API
========================

:mod:`zope.location.interfaces`
-------------------------------

.. automodule:: zope.location.interfaces

   .. autointerface:: ILocation
      :members:
      :member-order: bysource

   .. autointerface:: IContained
      :members:
      :member-order: bysource

   .. autointerface:: ILocationInfo
      :members:
      :member-order: bysource

   .. autointerface:: ISublocations
      :members:
      :member-order: bysource

   .. autointerface:: IRoot
      :members:
      :member-order: bysource

   .. autoexception:: LocationError
      :members:
      :member-order: bysource

:mod:`zope.location.location`
-----------------------------

.. automodule:: zope.location.location

   .. autoclass:: Location
      :members:
      :member-order: bysource

   .. autofunction:: locate

   .. autofunction:: located

   .. autofunction:: LocationIterator

   .. autofunction:: inside

   .. autoclass:: LocationProxy
      :members:
      :member-order: bysource

:mod:`zope.location.traversing`
-------------------------------

.. automodule:: zope.location.traversing

   .. autoclass:: LocationPhysicallyLocatable
    
      .. doctest::

         >>> from zope.interface.verify import verifyObject
         >>> from zope.location.interfaces import ILocationInfo
         >>> from zope.location.location import Location
         >>> from zope.location.traversing import LocationPhysicallyLocatable
         >>> info = LocationPhysicallyLocatable(Location())
         >>> verifyObject(ILocationInfo, info)
         True

      .. automethod:: getRoot

         .. doctest::

            >>> from zope.interface import directlyProvides
            >>> from zope.location.interfaces import IRoot
            >>> from zope.location.location import Location
            >>> from zope.location.traversing import LocationPhysicallyLocatable
            >>> root = Location()
            >>> directlyProvides(root, IRoot)
            >>> LocationPhysicallyLocatable(root).getRoot() is root
            True

            >>> o1 = Location(); o1.__parent__ = root
            >>> LocationPhysicallyLocatable(o1).getRoot() is root
            True

            >>> o2 = Location(); o2.__parent__ = o1
            >>> LocationPhysicallyLocatable(o2).getRoot() is root
            True

         We'll get a TypeError if we try to get the location fo a
         rootless object:

         .. doctest::

            >>> o1.__parent__ = None
            >>> LocationPhysicallyLocatable(o1).getRoot()
            Traceback (most recent call last):
            ...
            TypeError: Not enough context to determine location root
            >>> LocationPhysicallyLocatable(o2).getRoot()
            Traceback (most recent call last):
            ...
            TypeError: Not enough context to determine location root

         If we screw up and create a location cycle, it will be caught:

         .. doctest::

            >>> o1.__parent__ = o2
            >>> LocationPhysicallyLocatable(o1).getRoot()
            Traceback (most recent call last):
            ...
            TypeError: Maximum location depth exceeded, probably due to a a location cycle.

      .. automethod:: getPath

         .. doctest::

            >>> from zope.interface import directlyProvides
            >>> from zope.location.interfaces import IRoot
            >>> from zope.location.location import Location
            >>> from zope.location.traversing import LocationPhysicallyLocatable
            >>> root = Location()
            >>> directlyProvides(root, IRoot)
            >>> LocationPhysicallyLocatable(root).getPath()
            u'/'

            >>> o1 = Location(); o1.__parent__ = root; o1.__name__ = 'o1'
            >>> LocationPhysicallyLocatable(o1).getPath()
            u'/o1'

            >>> o2 = Location(); o2.__parent__ = o1; o2.__name__ = u'o2'
            >>> LocationPhysicallyLocatable(o2).getPath()
            u'/o1/o2'

         It is an error to get the path of a rootless location:

         .. doctest::

            >>> o1.__parent__ = None
            >>> LocationPhysicallyLocatable(o1).getPath()
            Traceback (most recent call last):
            ...
            TypeError: Not enough context to determine location root

            >>> LocationPhysicallyLocatable(o2).getPath()
            Traceback (most recent call last):
            ...
            TypeError: Not enough context to determine location root

         If we screw up and create a location cycle, it will be caught:

         .. doctest::

            >>> o1.__parent__ = o2
            >>> LocationPhysicallyLocatable(o1).getPath()
            Traceback (most recent call last):
            ...
            TypeError: Maximum location depth exceeded, """ \
                    """probably due to a a location cycle.

      .. automethod:: getParent

         .. doctest::

            >>> from zope.interface import directlyProvides
            >>> from zope.location.interfaces import IRoot
            >>> from zope.location.location import Location
            >>> from zope.location.traversing import LocationPhysicallyLocatable
            >>> root = Location()
            >>> directlyProvides(root, IRoot)
            >>> o1 = Location()
            >>> o2 = Location()

            >>> LocationPhysicallyLocatable(o2).getParent() # doctest: +ELLIPSIS
            Traceback (most recent call last):
            TypeError: ('Not enough context information to get parent', <zope.location.location.Location object at 0x...>)

            >>> o1.__parent__ = root
            >>> LocationPhysicallyLocatable(o1).getParent() == root
            True

            >>> o2.__parent__ = o1
            >>> LocationPhysicallyLocatable(o2).getParent() == o1
            True

      .. automethod:: getParents

         .. doctest::

            >>> from zope.interface import directlyProvides
            >>> from zope.interface import noLongerProvides
            >>> from zope.location.interfaces import IRoot
            >>> from zope.location.location import Location
            >>> from zope.location.traversing import LocationPhysicallyLocatable
            >>> root = Location()
            >>> directlyProvides(root, IRoot)
            >>> o1 = Location()
            >>> o2 = Location()
            >>> o1.__parent__ = root
            >>> o2.__parent__ = o1
            >>> LocationPhysicallyLocatable(o2).getParents() == [o1, root]
            True
            
            If the last parent is not an IRoot object, TypeError will be
            raised as statet before.
            
            >>> noLongerProvides(root, IRoot)
            >>> LocationPhysicallyLocatable(o2).getParents()
            Traceback (most recent call last):
            ...
            TypeError: Not enough context information to get all parents

      .. automethod:: getName

         .. doctest::

            >>> from zope.location.location import Location
            >>> from zope.location.traversing import LocationPhysicallyLocatable
            >>> o1 = Location(); o1.__name__ = u'o1'
            >>> LocationPhysicallyLocatable(o1).getName()
            u'o1'

      .. automethod:: getNearestSite

         .. doctest::

            >>> from zope.interface import directlyProvides
            >>> from zope.component.interfaces import ISite
            >>> from zope.location.interfaces import IRoot
            >>> from zope.location.location import Location
            >>> from zope.location.traversing import LocationPhysicallyLocatable
            >>> o1 = Location()
            >>> o1.__name__ = 'o1'
            >>> LocationPhysicallyLocatable(o1).getNearestSite()
            Traceback (most recent call last):
            ...
            TypeError: Not enough context information to get all parents

            >>> root = Location()
            >>> directlyProvides(root, IRoot)
            >>> o1 = Location()
            >>> o1.__name__ = 'o1'
            >>> o1.__parent__ = root
            >>> LocationPhysicallyLocatable(o1).getNearestSite() is root
            True
            
            >>> directlyProvides(o1, ISite)
            >>> LocationPhysicallyLocatable(o1).getNearestSite() is o1
            True
            
            >>> o2 = Location()
            >>> o2.__parent__ = o1
            >>> LocationPhysicallyLocatable(o2).getNearestSite() is o1
            True

   .. autoclass:: RootPhysicallyLocatable
    
      .. doctest::

         >>> from zope.interface.verify import verifyObject
         >>> from zope.location.interfaces import ILocationInfo
         >>> from zope.location.traversing import RootPhysicallyLocatable
         >>> info = RootPhysicallyLocatable(None)
         >>> verifyObject(ILocationInfo, info)
         True

      .. automethod:: getRoot

         No need to search for root when our context is already root :) 

         .. doctest::

            >>> from zope.location.traversing import RootPhysicallyLocatable
            >>> o1 = object()
            >>> RootPhysicallyLocatable(o1).getRoot() is o1
            True

      .. automethod:: getPath

         Root object is at the top of the tree, so always return ``/``. 

         .. doctest::

            >>> from zope.location.traversing import RootPhysicallyLocatable
            >>> o1 = object()
            >>> RootPhysicallyLocatable(o1).getPath()
            u'/'

      .. automethod:: getParent

         Returns None if the object is a containment root.
         Raises TypeError if the object doesn't have enough context to get the
         parent.

         .. doctest::

            >>> from zope.location.traversing import RootPhysicallyLocatable
            >>> o1 = object()
            >>> RootPhysicallyLocatable(o1).getParent() is None
            True

      .. automethod:: getParents

         There's no parents for the root object, return empty list.

         .. doctest::

            >>> from zope.location.traversing import RootPhysicallyLocatable
            >>> o1 = object()
            >>> RootPhysicallyLocatable(o1).getParents()
            []

      .. automethod:: getName

         Always return empty unicode string for the root object

         .. doctest::

            >>> from zope.location.traversing import RootPhysicallyLocatable
            >>> o1 = object()
            >>> RootPhysicallyLocatable(o1).getName()
            u''

      .. automethod:: getNearestSite
 
         Return object itself as the nearest site, because there's no
         other place to look for. It's also usual that the root is the
         site as well.

         .. doctest::

            >>> from zope.location.traversing import RootPhysicallyLocatable
            >>> o1 = object()
            >>> RootPhysicallyLocatable(o1).getNearestSite() is o1
            True
