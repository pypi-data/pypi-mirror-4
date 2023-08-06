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
__docformat__ = "reStructuredText"

from zope import interface
import zope.interface.common.mapping
from zope import component
from zope import schema
from zope import lifecycleevent

class ISynchronizableExtras(interface.common.mapping.IMapping):
    """A mapping of selected object attributes."""


class ISynchronizableAnnotations(interface.common.mapping.IMapping):
    """A mapping of synchronizable annotation namespaces."""

    def modify(target):
        """Modifies the target annotations.

        Transfers the synchronizable namespaces to the target annotations.
        Returns an lifecycleevent.interfaces.IModificationDescription
        if changes were detected, None othewise.
        """


class IObjectSynchronized(lifecycleevent.interfaces.IModificationDescription):
    """A unspecific modification description.

    Basically says that an object has changed during a sync
    operation. If you can say more specific things you should
    use other modification descriptions.
    """

class IRepository(interface.Interface):
    """A target system that stores objects as files or directories."""

    chunk_size = schema.Int(
        title=u"Chunk Size",
        description=u"The chunk size.",
        default=32768)

    case_insensitive = schema.Bool(
        title=u"Case Insensitive",
        description=u"Is this repository case insensitive?",
        default=False)

    def getMetadata():
        """Returns a metadata database for the repository.
        """

    def disambiguate(dirpath, name):
        """Disambiguates a name in a directory.
        """

    def dirname(path):
        """Returns the dirname."""

    def join(path, *names):
        """Returns a joined path."""

    def normalize(name):
        """Normalize a filename.
        """

    def encode(path, encoding=None):
        """Encodes a path in its normalized form."""

    def writeable(path):
        """Returns a writeable file handler."""

    def readable(path):
        """Returns a readable file handler."""


class IPickler(interface.Interface):
    """A pickler."""

    def dump(writeable):
        """Dumps a pickable object to a writeable file-like object."""


class IUnpickler(interface.Interface):
    """An unpickler."""

    def load(readable):
        """Loads a pickled object from a readable file-like object."""


class IEntryId(interface.Interface):
    """Returns an id that can be saved in a metadata database.

    The id must be 'stringifiable'.
    """

    def __str__():
        """Returns a string representation.

        The encoding should be 'UTF-8'.
        """


class IPersistentIdGenerator(interface.Interface):
    """Generates a pickable persistent references."""

    def id(self, obj):
        """Returns a persistent reference."""


class IPersistentIdLoader(interface.Interface):

    def load(self, id):
        """Resolves a persistent reference."""


class IWriteable(interface.Interface):
    """A writeable file handle."""

    def write(data):
        """Writes the data."""

    def close():
        """Closes the file-like object.

        Ensures that pending data are written.
        """


class IReadable(interface.Interface):
    """A readable file handle."""

    def read(bytes=None):
        """Reads the number of bytes or all data if bytes is None."""

    def close():
        """Closes the file handle."""


class ISyncTask(interface.Interface):
    """Base interface for ICheckout, ICommit, and ICheck.

    The repository may be a filesystem, an archive, a database,
    or something else that is able to store serialized data.
    """

    repository = schema.Object(
        IRepository,
        title=u"Repository",
        description=u"The repository that contains the serialized data.")

    context = schema.Object(
        interface.Interface,
        title=u"Context",
        description=u"Context of reference")

    def __init__(getSynchronizer, repository, context=None):
        """Inits the task with a getSynchronizer lookup function,
        a repository, and an optional context.
        """


class ICheckout(ISyncTask):
    """Checkout objects from a content space to a repository.
    """

    def perform(obj, name, location=''):
        """Check an object out to the repository.

        obj -- The object to be checked out

        name -- The name of the object

        location -- The directory or path where the object will go
        """


class ICheckin(ISyncTask):
    """Import objects from the repository to a content space.
    """

    def perform(obj, name, location=''):
        """Performs a checkin.

        obj -- The object to be checked in

        name -- The name of the object

        location -- The location where the object will go

        Raises a ``SynchronizationError`` if the object
        already exists at the given location.
        """


class ICheck(ISyncTask):
    """Check that the repository is consistent with the object database."""

    def perform(container, name, fspath):
        """Compare an object or object tree from a repository.

        If the originals in the repository are not uptodate, errors
        are reported by a errors() call.

        Invalid object names are reported by raising
        ``SynchronizationError``.
        """

    def errors():
        """Returns a list of paths with errors."""


class ICommit(ISyncTask):
    """Commits a repository to a content space."""

    def perform(container, name, fspath, context=None):
        """Synchronize an object or object tree from a repository.
        """


class IFileSystemRepository(IRepository):
    """A filesystem repository.

    Stores the data in a directory tree on the filesystem.
    """


class IArchiveRepository(IRepository):
    """A repository that stores the data in a single file."""

    def iterPaths():
        """Iterates over all paths in the archive."""

class IVersionControlRepository(IRepository):
    """A repository that stores the data in a version control system."""

class ISVNRepository(IRepository):
    """A repository that stores the data in a subversion checkout."""


class ISynchronizerFactory(component.interfaces.IFactory):
    """A factory for synchronizer, i.e. serializers/de-serializers.

    The factory should be registered as a named utility with
    the dotted name of the adapted class as the lookup key.

    The default factory should be registered without a name.

    The call of the factory should return

    - an `IDirectorySynchronizer` adapter for the object if the
      object is represented as a directory.

    - an `IFileSynchronizer` adapter for the object if the
      object is represented as a file.
    """


class ISerializer(interface.Interface):
    """Base interface for object serializer."""

    def getObject():
        """Return the serializable entry."""

    def metadata():
        """Returns a mapping with metadata.

        The keys must be attribute names, the values utf-8 encoded strings.
        """

    def annotations():
        """Return annotations for the entry.

        Returns None if the serializer provides
        it's own representation
        """

    def extras():
        """Return extra data for the entry.

        Returns None if the serializer provides it's own
        representation of extras.
        """


class IDeserializer(interface.Interface):
    """The inverse operator of an ISerializer.

    Deserializer consume serialized data and provide
    write access to parts of the deserialized objects.
    """

    def setmetadata(metadata):
        """Sets entry metadata.

        Returns an lifecycleevent.interfaces.IModificationDescription
        if relevant changes were detected, None othewise.
        """

    def setannotations(annotations):
        """Sets deserialized annotations.

        Returns an lifecycleevent.interfaces.IModificationDescription
        if relevant changes were detected, None othewise.
        """

    def setextras(extras):
        """Sets deserialized extra data.

        Returns an lifecycleevent.interfaces.IModificationDescription
        if relevant changes were detected, None othewise.
        """


class ISynchronizer(ISerializer, IDeserializer):
    """A base interface for synchronizers."""


class IFileSerializer(ISerializer):
    """Writes data to a file-like object."""

    def dump(writeable):
        """Dump the file content to a writeable file handle."""


class IFileDeserializer(IDeserializer):
    """Reads data from a file-like object."""

    def load(readable):
        """Reads serialized file content."""


class IFileSynchronizer(IFileSerializer, IFileDeserializer):
    """A sycnronizer for file-like objects."""


class IDefaultSynchronizer(IFileSynchronizer):
    """A serializer that uses an IPickler."""


class IDirectorySerializer(ISerializer):
    """Provides access to a dirctory listing."""

    def __getitem__(key, value):
        """Gets an item."""

    def iteritems():
        """Return an iterable directory listing of name, obj tuples."""


class IDirectoryDeserializer(IDeserializer):
    """Writes deserialized data into a directory-like object."""

    def __setitem__(key, value):
        """Sets an item."""

    def __delitem__(key):
        """Deletes an item."""


class IDirectorySynchronizer(ISynchronizer,
                                IDirectorySerializer, IDirectoryDeserializer):
    """A synchronizer for directory-like objects."""

    def traverseName(name):
        """Traverses the name."""


class IObjectGenerator(interface.Interface):
    """A generator for objects with a special create protocol."""

    def create(context, name):
        """Creates the object in the given context."""


class IFileGenerator(interface.Interface):
    """A generator that applies if no other file deserializers can be found."""

    def create(context, readable, extension=None):
        """Creates a new file object and initializes it with the readable data.

        Uses the optional file extension to determine the file type.
        """

    def load(file, readable):
        """Consumes readable data for the generated file."""


class IDirectoryGenerator(IObjectGenerator):
    """A generator that applies if no other directory factories can be found."""


def getSynchronizer(obj):
    """Returns the class based synchronizer or the default synchronizer."""

