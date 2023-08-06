##############################################################################
#
# Copyright (c) 2001, 2002 Zope Corporation and Contributors.
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
"""Interfaces for filesystem synchronization.

$Id: interfaces.py 73003 2007-03-06 10:34:19Z oestermeier $
"""

from zope import interface
from zope import component
from zope import annotation
from zope import lifecycleevent

from zope.dottedname.resolve import resolve
from zope.filerepresentation.interfaces import IFileFactory
from zope.filerepresentation.interfaces import IDirectoryFactory

import interfaces

def dottedname(klass):
    return "%s.%s" % (klass.__module__, klass.__name__)


class MissingSynchronizer(Exception):
    pass


class Extras(dict):
    """A serializable mapping of object attributes."""

    interface.implements(interfaces.ISynchronizableExtras)


class SynchronizableAnnotations(dict):
    """A serializable mapping of annotations."""

    interface.implements(interfaces.ISynchronizableAnnotations)
    component.adapts(annotation.interfaces.IAnnotations)

    def modify(self, target):
        """Transfers the namespaces to the target annotations.

        Returns a lifecycleevent.interfaces.ISequence modification
        descriptor or None if nothing changed.
        """
        target.update(self)
        modified = []
        for key, value in self.items():
            old = interfaces.IPickler(target.get(key)).dumps()
            target[key] = value
            if old != interfaces.IPickler(value).dumps():
                modified.append(key)
        if modified:
            return lifecycleevent.Sequence(
                        annotation.interfaces.IAnnotations,
                        modified)
        return None

class Synchronizer(object):
    """A convenient base class for serializers."""

    interface.implements(interfaces.ISynchronizer)

    def __init__(self, context):
        self.context = context

    def getObject(self):
        return self.context

    def metadata(self):
        """Returns a mapping for the metadata entries."""
        result = dict(factory=dottedname(self.context.__class__))
        ifaces = interface.directlyProvidedBy(self.context)
        if ifaces:
            result['provides'] = ' '.join([dottedname(i) for i in ifaces])
        return result

    def setmetadata(self, metadata):
        """Loads metadata from a dict.

        Specializations should return an IModificationDescription
        if a ModifiedEvent should be thrown.
        """
        provides = metadata.get('provides')
        if provides:
            for dottedname in provides.split():
                iface = resolve(dottedname)
                interface.alsoProvides(self.context, iface)
        return None

    def extras(self):
        return None

    def annotations(self):
        ann = annotation.interfaces.IAnnotations(self.context, None)
        if ann is not None:
            return interfaces.ISynchronizableAnnotations(ann, None)

    def setannotations(self, annotations):
        """Consumes de-serialized annotations."""
        ann = annotation.interfaces.IAnnotations(self.context, None)
        if ann is not None:
            sann = interfaces.ISynchronizableAnnotations(annotations, None)
            if sann is not None:
                return sann.modify(ann)

    def setextras(self, extras):
        """Consumes de-serialized extra attributes.

        Returns an unspecific IModificationDescription.
        Application specific adapters may provide more informative
        descriptors.
        """

        modified = []
        for key, value in extras.iteritems():
            if hasattr(self.context, key):
                if getattr(self.context, key) != value:
                    modified.append(key)
                    setattr(self.context, key, value)
        if modified:
            return lifecycleevent.Attributes(None, modified)
        return None


class FileSynchronizer(Synchronizer):
    """A convenient base class for file serializers."""

    interface.implements(interfaces.IFileSynchronizer)

    def dump(self, writeable):
        pass

    def load(self, readable):
        pass


class DefaultSynchronizer(FileSynchronizer):
    """A synchronizer that stores an object as an xml pickle."""

    interface.implements(interfaces.IDefaultSynchronizer)

    def __init__(self, context):
        self.context = context

    def metadata(self):
        """Returns None.

        A missing factory indicates that the object has
        has to be unpickled.
        """
        return None

    def extras(self):
        """Returns None.

        A pickle is self contained."""
        return None

    def annotations(self):
        """Returns None.

        The annotations are already stored in the pickle.
        This is only the right thing if the annotations are
        stored in the object's attributes (such as IAttributeAnnotatable);
        if that's not the case, then either this method needs to be
        overridden or this class shouldn't be used."""
        return None

    def dump(self, writeable):
        """Dumps the xml pickle."""
        interfaces.IPickler(self.context).dump(writeable)

    def load(self, readable):
        raise NotImplementedError


class DirectorySynchronizer(Synchronizer):
    """A serializer that stores objects as directory-like objects.
    """
    interface.implements(interfaces.IDirectorySynchronizer)

    def __getitem__(self, name):
        """Traverses the name in the given context.
        """
        return self.context[name]

    def iteritems(self):
        return self.context.items()

    def update(self, items):
        """Updates the context."""
        self.context.update(items)

    def __setitem__(self, name, obj):
        """Sets the item."""
        self.context[name] = obj

    def __delitem__(self, name):
        """Deletes ths item."""
        del self.context[name]


class FileGenerator(object):
    """A generator that creates file-like objects
    from a serialized representation.

    Should be registered as the IFileGenerator utility
    and be used if no other class-based serializer can be found.
    """

    interface.implements(interfaces.IFileGenerator)

    def create(self, location, name, extension):
        """Creates a file.

        This implementation uses the registered zope.filerepresentation adapters.
        """
        factory = component.queryAdapter(location, IFileFactory, extension)
        if factory is None:
            factory = IFileFactory(location, None)
        if factory is not None:
            return factory(name, None, '')

    def load(self, obj, readable):
        obj.data = readable.read()

class DirectoryGenerator(object):
    """A generator that creates a directory-like object
    from a serialized representation.

    Should be registered as the IDirectoryGenerator utility
    and be used if no other class-based serializer can be found.
    """

    interface.implements(interfaces.IDirectoryGenerator)

    def create(self, location, name):
        """Creates a directory like object.

        This implementation uses the registered zope.filerepresentation adapters.
        """

        factory = component.queryAdapter(location, IDirectoryFactory)
        if factory is None:
            factory = IDirectoryFactory(location, None)
        if factory is not None:
            return factory(name)


def getSynchronizer(obj, raise_error=False):
    """Looks up a synchronizer.

    Sometimes no serializer might be defined or sometimes access
    to a serializer may be forbidden. We return None in those cases.

    Those cases may be unexpected and it may be a problem that
    the data are not completely serialized. If raise_error is True
    we raise a MissingSynchronizer in those cases.
    """
    dn = dottedname(obj.__class__)
    factory = component.queryUtility(interfaces.ISynchronizerFactory, name=dn)
    if factory is None:
        factory = component.queryUtility(interfaces.ISynchronizerFactory)
    if factory is None:
        if raise_error:
            raise MissingSynchronizer(dn)
        return None
    return factory(obj)
