##############################################################################
#
# Copyright (c) 2007 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Pickle support functions for fssync.

Defines a standard pickle format and an XML variant thereof.
The pickles preserve persistent references.

The default implementation generate pickles that understand their location in
the object tree without causing the entire tree to be stored in the
pickle.  Persistent objects stored inside the outermost object are
stored entirely in the pickle, and objects stored outside by outermost
object but referenced from within are stored as persistent references.
The parent of the outermost object is treated specially so that the
pickle can be 'unpacked' with a new parent to create a copy in the new
location; unpacking a pickle containing a parent reference requires
passing an object to use as the parent as the second argument to the
`loads()` function.  The name of the outermost object is not stored in
the pickle unless it is stored in the object.

>>> root = TLocation()
>>> interface.directlyProvides(root, IContainmentRoot)
>>> o1 = DataLocation('o1', root, 12)
>>> o2 = DataLocation('o2', root, 24)
>>> o3 = DataLocation('o3', o1, 36)
>>> o4 = DataLocation('o4', o3, 48)
>>> o1.foo = o2

We must register the path id generator and loader:

>>> component.provideAdapter(PathPersistentIdGenerator)
>>> component.provideAdapter(PathPersistentLoader)

>>> s = StandardPickler(o1).dumps()
>>> unpickler = StandardUnpickler(o1.__parent__)
>>> c1 = unpickler.loads(s)
>>> c1 is not o1
1
>>> c1.data == o1.data
1
>>> c1.__parent__ is o1.__parent__
1
>>> c1.foo is o2
1
>>> c3 = c1.o3
>>> c3 is o3
0
>>> c3.__parent__ is c1
1
>>> c3.data == o3.data
1
>>> c4 = c3.o4
>>> c4 is o4
0
>>> c4.data == o4.data
1
>>> c4.__parent__ is c3
1

See README.txt for an example how to replace paths by different ids.


$Id: pickle.py 73003 2007-03-06 10:34:19Z oestermeier $
"""
__docformat__ = 'restructuredtext'

from cStringIO import StringIO
from cPickle import Unpickler

from zope import component
from zope import interface
from zope import traversing
from zope import location

from zope.location.interfaces import ILocation
from zope.location.traversing import LocationPhysicallyLocatable
from zope.traversing.interfaces import IContainmentRoot

from zope.xmlpickle import xmlpickle

import interfaces

PARENT_MARKER = ".."

def getPath(obj):
    path = LocationPhysicallyLocatable(obj).getPath()
    return path.encode('utf-8')
    
class PathPersistentIdGenerator(object):
    """Uses traversal paths as persistent ids.

    >>> root = TLocation()
    >>> interface.directlyProvides(root, IContainmentRoot)
    >>> o1 = TLocation(); o1.__parent__ = root; o1.__name__ = 'o1'
    >>> o2 = TLocation(); o2.__parent__ = root; o2.__name__ = 'o2'
    >>> o3 = TLocation(); o3.__parent__ = o1; o3.__name__ = 'o3'
    >>> root.o1 = o1
    >>> root.o2 = o2
    >>> o1.foo = o2
    >>> o1.o3 = o3

    >>> gen = PathPersistentIdGenerator(StandardPickler(o1))
    >>> gen.id(root)
    '..'
    >>> gen.id(o2)
    '/o2'
    >>> gen.id(o3)
    >>> gen.id(o1)

    >>> gen = PathPersistentIdGenerator(StandardPickler(o3))
    >>> gen.id(root)
    '/'

    """

    interface.implements(interfaces.IPersistentIdGenerator)
    component.adapts(interfaces.IPickler)

    root = None
    
    def __init__(self, pickler):
        
        self.pickler = pickler
        top = self.location = pickler.context
        self.parent = getattr(top, "__parent__", None)
        if ILocation.providedBy(top):
            try:
                self.root = LocationPhysicallyLocatable(top).getRoot()
            except TypeError:
                pass

    def id(self, object):
        if self.parent is None:
            return None

        if ILocation.providedBy(object):
            if location.inside(object, self.location):
                return None
            elif object is self.parent:
                # emit special parent marker
                return PARENT_MARKER
            elif location.inside(object, self.root):
                return getPath(object)
            elif object.__parent__ is None:
                return None
            raise ValueError(
                "object implementing ILocation found outside tree")
        else:
            return None


class PathPersistentLoader(object):
    """Loads objects from paths.

    Uses path traversal if the context of the adapted 
    Unpickler is locatable."""

    interface.implements(interfaces.IPersistentIdLoader)
    component.adapts(interfaces.IUnpickler)

    def __init__(self, unpickler):
        context = self.parent = unpickler.context
        self.root = None
        if ILocation.providedBy(context):
            locatable = LocationPhysicallyLocatable(context)
            __traceback_info__ = (context, locatable)
            try:
                self.root = locatable.getRoot()
            except TypeError:
                pass
        if self.root is not None:
            traverser = traversing.interfaces.ITraverser(self.root)
            self.traverse = traverser.traverse

    def load(self, path):
        """Loads the object.
        
        Returns the context of the adapted Unpickler if a PARENT_MARKER
        is found.
        """

        if path == PARENT_MARKER:
            return self.parent
        if path[:1] == "/":
            # outside object:
            if path == "/":
                return self.root
            else:
                return self.traverse(path[1:])
        raise ValueError("unknown persistent object reference: %r" % path)


class StandardPickler(object):
    """A pickler that uses the standard pickle format.
    
    Calls an IPersistentIdGenerator multi adapter.
    
    Uses the _PicklerThatSortsDictItems to ensure that pickles
    are repeatable.
    """

    interface.implements(interfaces.IPickler)
    component.adapts(interface.Interface)

    def __init__(self, context):
        self.context = context

    def dump(self, writeable):
        pickler = xmlpickle._PicklerThatSortsDictItems(writeable, 0)
        generator = interfaces.IPersistentIdGenerator(self, None)
        if generator is not None:
            pickler.persistent_id = generator.id
        pickler.dump(self.context)

    def dumps(self):
        stream = StringIO()
        self.dump(stream)
        return stream.getvalue()


class StandardUnpickler(object):
    """An unpickler for a standard pickle format.
    
    Calls an IPersistentIdLoader multi adapter.
    """

    interface.implements(interfaces.IUnpickler)
    component.adapts(interface.Interface)

    def __init__(self, context):
        self.context = context
    
    def load(self, readable):
        unpickler = Unpickler(readable)
        loader = interfaces.IPersistentIdLoader(self, None)
        if loader is not None:
            unpickler.persistent_load = loader.load
        return unpickler.load()

    def loads(self, pickle):
        return self.load(StringIO(pickle))


class XMLPickler(StandardPickler):
    """A pickler that uses a XML format.
    
    The current implementation assumes that the pickle can be
    hold in memory completely.
    """

    interface.implements(interfaces.IPickler)
    component.adapts(interface.Interface)

    def dump(self, writeable):
        stream = StringIO()
        super(XMLPickler, self).dump(stream)
        p = stream.getvalue()
        writeable.write(xmlpickle.toxml(p))


class XMLUnpickler(StandardUnpickler):
    """A pickler that uses a XML format.
    
    The current implementation assumes that the pickle can be
    hold in memory completely.
    """

    def load(self, readable):
        pickle = xmlpickle.fromxml(readable.read())
        return super(XMLUnpickler, self).load(StringIO(pickle))



from zope.location.location import Location


class TLocation(Location):
    """Simple traversable location used in examples."""

    interface.implements(traversing.interfaces.ITraverser)

    def traverse(self, path, default=None, request=None):
        o = self
        for name in path.split(u'/'):
           o = getattr(o, name)
        return o


class DataLocation(TLocation):
    """Sample data container class used in doctests."""

    def __init__(self, name, parent, data):
        self.__name__ = name
        self.__parent__ = parent
        if parent is not None:
            setattr(parent, name, self)
        self.data = data
        super(DataLocation, self).__init__()
