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
"""Synchronize content objects with a repository.

$Id: syncer.py 73003 2007-03-06 10:34:19Z oestermeier $
"""
import os

import zope.interface
import zope.component
import zope.traversing.api
import zope.event
import zope.lifecycleevent
import zope.dottedname.resolve

import metadata
import interfaces
import synchronizer
import fsutil

from synchronizer import dottedname

class SynchronizationError(Exception):
    pass

@zope.component.adapter(zope.interface.Interface)
@zope.interface.implementer(interfaces.IEntryId)
def EntryId(obj):
    try:
        path = zope.traversing.api.getPath(obj)
        return path.encode('utf-8')
    except (TypeError, KeyError, AttributeError):
        # this case can be triggered for persistent objects that don't
        # have a name in the content space (annotations, extras)
        return None


class ObjectSynchronized(object):
    """A default modification description for synchronized objects."""

    zope.interface.implements(interfaces.IObjectSynchronized)

class SyncTask(object):
    """Convenient base class for synchronization tasks."""

    def __init__(self, getSynchronizer,
                       repository,
                       context=None):
        self.getSynchronizer = getSynchronizer
        self.repository = repository
        self.context = context

class Checkout(SyncTask):
    """Checkout of a content space into a repository."""

    zope.interface.implements(interfaces.ICheckout)

    def perform(self, ob, name, location=''):
        """Check an object out.

        ob -- The object to be checked out

        name -- The name of the object

        location -- The directory or path where the object will go
        """
        root = dict()
        self.context = root[name] = ob
        self.dump(synchronizer.DirectorySynchronizer(root), location)

    def serializableItems(self, items, dirpath):
        """Returns items which have synchronizer.

        Returns a tuple of disambiguated name, original key, and synchronizer.
        """
        result = []
        repository = self.repository
        if items is not None:
            for key, value in items:
                synchronizer = self.getSynchronizer(value, raise_error=False)
                if synchronizer is not None:
                    name = repository.disambiguate(dirpath, key)
                    result.append((name, key, synchronizer))
        return sorted(result)

    def dump(self, synchronizer, path):
        if synchronizer is None:
            return
        if interfaces.IDirectorySynchronizer.providedBy(synchronizer):
            items = self.serializableItems(synchronizer.iteritems(), path)
            self.dumpSpecials(path, items)
            for name, key, s in items:   # recurse down the tree
                self.dump(s, self.repository.join(path, name))
        elif interfaces.IFileSynchronizer.providedBy(synchronizer):
            fp = self.repository.writeable(path)
            synchronizer.dump(fp)
            fp.close()
        else:
            raise SynchronizationError("invalid synchronizer")

    def dumpMetadata(self, epath, entries):
        xml = metadata.dump_entries(entries)
        fp = self.repository.writeable(epath)
        fp.write(xml)
        fp.close()

    def dumpSpecials(self, path, items):
        entries = {}
        repository = self.repository
        zdir = repository.join(path, '@@Zope')
        epath = repository.join(zdir, 'Entries.xml')

        for name, key, s in items:
            obj = s.getObject()
            entry = dict(type=typeIdentifier(obj))
            metadata = s.metadata()
            if metadata:
                for k, v in metadata.items():
                    if v:
                        entry[k] = v
            objid = getEntryId(obj)
            if objid:
                entry['id'] = str(objid)
            if key != name:
                entry['key'] = key
            entry['keytype'] = dottedname(key.__class__)
            entries[name] = entry

        if path:
            self.dumpMetadata(epath, entries)

        adir = repository.join(zdir, 'Annotations')
        for name, key, s in items:
            dir = repository.join(adir, name)
            annotations = s.annotations()
            if annotations:
                synchronizer = self.getSynchronizer(annotations)
                if synchronizer is not None:
                    self.dump(synchronizer, dir)

        edir = repository.join(zdir, 'Extra')
        for name, key, s in items:
            dir = repository.join(edir, name)
            extras = s.extras()
            if extras:
                synchronizer = self.getSynchronizer(extras)
                if synchronizer is not None:
                    self.dump(synchronizer, dir)

        if not path:
            self.dumpMetadata(epath, entries)


class Exceptions(Exception):
    # We use this to pluralize "Exception".
    pass


class Commit(SyncTask):
    """Commit changes from a repository to the object database.

    The repository's originals must be consistent with the object
    database; this should be checked beforehand by a `Check` instance
    with the same arguments.
    """

    zope.interface.implements(interfaces.ICommit)

    debug = False

    def __init__(self, getSynchronizer, repository):
        super(Commit, self).__init__(getSynchronizer, repository)
        self.metadata = self.repository.getMetadata()
        self.errors = []

    def perform(self, container, name, fspath):
        callbacks = []
        add_callback = callbacks.append
        self.synchronize(container, name, fspath, add_callback)

        # check for errors
        if self.errors:
            if len(self.errors) == 1:
                raise Exception(self.errors[0])
            else:
                raise Exceptions("\n    ".join([""] + self.errors))

        # process callbacks
        passes = 0
        callbacks = [cb for cb in callbacks if cb is not None]
        while passes < 10 and callbacks:
            new_callbacks = []
            for callback in callbacks:
                new_callbacks.append(callback())
            callbacks = [cb for cb in new_callbacks if cb is not None]
            passes += 1

        # fail if there are still callbacks after 10 passes. this
        # suggests an infinate loop in callback creation.
        if callbacks:
            raise SynchronizationError(
                'Too many synchronizer callback passes %s' % callbacks)

    def synchronize(self, container, name, fspath, add_callback):
        """Synchronize an object or object tree from a repository.

        ``SynchronizationError`` is raised for errors that can't be
        corrected by a update operation, including invalid object
        names.
        """
        self.context = container
        modifications = []
        if invalidName(name):
            raise SynchronizationError("invalid separator in name %r" % name)

        if not name:
            self.synchDirectory(container, fspath, add_callback)
        else:
            synchronizer = self.getSynchronizer(container)
            key = originalKey(fspath, name, self.metadata)
            try:
                traverseKey(container, key)
            except:
                try:
                    self.synchNew(container, key, fspath, add_callback)
                except Exception, e:
                    self.errors.append('%s: %s' % (
                        fspath, ', '.join(repr(x) for x in e.args)))
                    return
            else:
                try:
                    modified = self.synchOld(container, key, fspath,
                        add_callback)
                except Exception, e:
                    self.errors.append('%s: %s' % (
                        fspath, ', '.join(repr(x) for x in e.args)))
                    return
                if modified:
                    modifications.append(modified)
            # Now update extra and annotations
            try:
                obj = traverseKey(container, key)
            except:
                pass
            else:
                metadata = self.metadata.getentry(fspath)
                synchronizer = self.getSynchronizer(obj)
                modified = synchronizer.setmetadata(metadata)
                if modified:
                    modifications.append(modified)

                extrapath = fsutil.getextra(fspath)
                if self.repository.exists(extrapath):
                    extras = synchronizer.extras()
                    extras = self.synchSpecials(extrapath, extras, add_callback)
                    modified = synchronizer.setextras(extras)
                    if modified:
                        modifications.append(modified)

                annpath = fsutil.getannotations(fspath)
                if self.repository.exists(annpath):
                    annotations = synchronizer.annotations()
                    annotations = self.synchSpecials(annpath, annotations,
                                                     add_callback)
                    modified = synchronizer.setannotations(annotations)
                    if modified:
                        modifications.append(modified)

            if modifications:
                zope.event.notify(
                    zope.lifecycleevent.ObjectModifiedEvent(
                        obj,
                        *modifications))


    def synchSpecials(self, fspath, specials, add_callback):
        """Synchronize an extra or annotation mapping."""
        md = self.metadata.getmanager(fspath)
        entries = md.entries
        synchronizer = self.getSynchronizer(specials)
        if interfaces.IDirectorySynchronizer.providedBy(synchronizer):
            for name, entry in entries.items():
                path = self.repository.join(fspath, name)
                self.synchronize(specials, name, path, add_callback)
        else:
            if interfaces.IDefaultSynchronizer.providedBy(synchronizer):
                fp = self.repository.readable(fspath)
                unpickler = interfaces.IUnpickler(self.context)
                specials = unpickler.load(fp)
                fp.close()
            elif interfaces.IFileSynchronizer.providedBy(synchronizer):
                fp = self.repository.readable(fspath)
                add_callback(synchronizer.load(fp))
                fp.close()

        return specials

    def synchDirectory(self, container, fspath, add_callback):
        """Helper to synchronize a directory."""
        adapter = self.getSynchronizer(container)
        nameset = {}
        if interfaces.IDirectorySynchronizer.providedBy(adapter):
            for key, obj in adapter.iteritems():
                nameset[key] = self.repository.join(fspath, key)
        else:
            # Annotations, Extra
            for key in container:
                nameset[key] = self.repository.join(fspath, key)
        for name in self.metadata.getnames(fspath):
            nameset[name] = self.repository.join(fspath, name)

        # Sort the list of keys for repeatability
        names_paths = nameset.items()

        names_paths.sort()
        subdirs = []
        # Do the non-directories first.
        # This ensures that the objects are created before dealing
        # with Annotations/Extra for those objects.
        for name, path in names_paths:
            if self.repository.isdir(path):
                subdirs.append((name, path))
            else:
                self.synchronize(container, name, path, add_callback)
        # Now do the directories
        for name, path in subdirs:
            self.synchronize(container, name, path, add_callback)

    def synchNew(self, container, name, fspath, add_callback):
        """Helper to synchronize a new object."""
        entry = self.metadata.getentry(fspath)
        if entry:
            # In rare cases (e.g. if the original name and replicated name
            # differ and the replica has been deleted) we can get
            # something apparently new that is marked for deletion. Since the
            # names are provided by the synchronizer we must at least
            # inform the synchronizer.
            if entry.get("flag") == "removed":
                self.deleteItem(container, name)
                return
            obj = self.createObject(container, name, entry, fspath,
                                    add_callback)
            synchronizer = self.getSynchronizer(obj)
            if interfaces.IDirectorySynchronizer.providedBy(synchronizer):
                self.synchDirectory(obj, fspath, add_callback)

    def synchOld(self, container, name, fspath, add_callback):
        """Helper to synchronize an existing object."""

        modification = None
        entry = self.metadata.getentry(fspath)
        if entry.get("flag") == "removed":
            self.deleteItem(container, name)
            return
        if not entry:
            # This object was not included on the filesystem; skip it
            return
        key = originalKey(fspath, name, self.metadata)
        obj = traverseKey(container, key)
        synchronizer = self.getSynchronizer(obj)
        if interfaces.IDirectorySynchronizer.providedBy(synchronizer):
            self.synchDirectory(obj, fspath, add_callback)
        else:
            type = entry.get("type")
            if type and typeIdentifier(obj) != type:
                self.createObject(container, key, entry, fspath, add_callback,
                                  replace=True)
            else:
                original_fn = fsutil.getoriginal(fspath)
                if self.repository.exists(original_fn):
                    original = self.repository.readable(original_fn)
                    replica = self.repository.readable(fspath)
                    new = not self.repository.compare(original, replica)
                else:
                    # value appears to exist in the object tree, but
                    # may have been created as a side effect of an
                    # addition in the parent; this can easily happen
                    # in the extra or annotation data for an object
                    # copied from another using "zsync copy" (for
                    # example)
                    new = True
                if new:
                    if not entry.get("factory"):
                        # If there's no factory, we can't call load
                        self.createObject(container, key, entry, fspath,
                                          add_callback, True)
                        obj = traverseKey(container, key)
                        modification = ObjectSynchronized()
                    else:
                        fp = self.repository.readable(fspath)
                        modified = not compare(fp, synchronizer)
                        if modified:
                            fp.seek(0)
                            add_callback(synchronizer.load(fp))
                            modification = ObjectSynchronized()
                        fp.close()
        return modification

    def createObject(self, container, name, entry, fspath, add_callback,
                     replace=False):
        """Helper to create a deserialized object."""
        factory_name = entry.get("factory")
        type = entry.get("type")
        isdir = self.repository.isdir(fspath)
        added = False
        if factory_name:
            generator = zope.component.queryUtility(interfaces.IObjectGenerator,
                                                        name=factory_name)
            if generator is not None:
                obj = generator.create(container, name)
                added = True
            else:
                try:
                    obj = resolveDottedname(factory_name)()
                except TypeError:
                    raise fsutil.Error("Don't know how to create %s" % factory_name)
            synchronizer = self.getSynchronizer(obj)
            if interfaces.IDefaultSynchronizer.providedBy(synchronizer):
                fp = self.repository.readable(fspath)
                unpickler = interfaces.IUnpickler(self.context)
                obj = unpickler.load(fp)
                fp.close()
            elif interfaces.IFileSynchronizer.providedBy(synchronizer):
                fp = self.repository.readable(fspath)
                add_callback(synchronizer.load(fp))
                fp.close()
        elif type:
            fp = self.repository.readable(fspath)
            unpickler = interfaces.IUnpickler(self.context)
            obj = unpickler.load(fp)
        else:
            if isdir:
                generator = zope.component.queryUtility(
                    interfaces.IDirectoryGenerator)
            else:
                generator = zope.component.queryUtility(
                    interfaces.IFileGenerator)
                isuffix = name.rfind(".")
                if isuffix >= 0:
                    suffix = name[isuffix:]
                else:
                    suffix = "."

            if generator is None:
                msg = "Don't know how to create object for %s"
                raise fsutil.Error(msg % fspath)

            if isdir:
                obj = generator.create(container, name)
            else:
                obj = generator.create(container, name, suffix)
                fp = self.repository.readable(fspath)
                if obj is None:
                    pickler = interfaces.IUnpickler(self.context)
                    obj = pickler.load(fp)
                else:
                    add_callback(generator.load(obj, fp))
                fp.close()

        if not added:
            self.setItem(container, name, obj, replace)
        return obj

    def setItem(self, container, key, obj, replace=False):
        """Helper to set an item in a container.

        Uses the synchronizer for the container if a synchronizer is available.
        """

        dir = self.getSynchronizer(container)
        if interfaces.IDirectorySynchronizer.providedBy(dir):
            if not replace:
                zope.event.notify(zope.lifecycleevent.ObjectCreatedEvent(obj))
            if replace:
                del dir[key]
            dir[key] = obj
        else:
            container[key] = obj

    def deleteItem(self, container, key):
        """Helper to delete an item from a container.

        Uses the synchronizer if possible.
        """

        dir = self.getSynchronizer(container)
        if interfaces.IDirectorySynchronizer.providedBy(dir):
            del dir[key]
        else:
            del container[key]


class Checkin(Commit):

    zope.interface.implements(interfaces.ICheckin)

    def perform(self, container, name, fspath):
        """Checkin a new object tree.

        Raises a ``SynchronizationError`` if the name already exists
        in the object database.
        """
        callbacks = []
        add_callback = callbacks.append

        self.context = container    # use container as context of reference
        self.metadata.added()
        try:
            traverseKey(container, name)
        except:
            self.synchronize(container, name, fspath, add_callback)
        else:
            raise SynchronizationError("object already exists %r" % name)

        # check for errors
        if self.errors:
            if len(self.errors) == 1:
                raise Exception(self.errors[0])
            else:
                raise Exceptions("\n    ".join([""] + self.errors))

        # process callbacks
        passes = 0
        callbacks = [cb for cb in callbacks if cb is not None]
        while passes < 10 and callbacks:
            new_callbacks = []
            for callback in callbacks:
                new_callbacks.append(callback())
            callbacks = [cb for cb in new_callbacks if cb is not None]
            passes += 1

        # fail if there are still callbacks after 10 passes. this
        # suggests an infinate loop in callback creation.
        if callbacks:
            raise SynchronizationError(
                'Too many synchronizer callback passes %s' % callbacks)



class Check(SyncTask):
    """Check that a repository is consistent with the object database.
    """

    zope.interface.implements(interfaces.ICheck)

    def __init__(self, getSynchronizer, repository,
                                        raise_on_conflicts=False):
        super(Check, self).__init__(getSynchronizer, repository)
        self.metadata = repository.getMetadata()
        self.conflicts = []
        self.raise_on_conflicts = raise_on_conflicts

    def errors(self):
        """Return a list of errors (conflicts).

        The return value is a list of filesystem pathnames for which
        a conflict exists.  A conflict usually refers to a file that
        was modified on the filesystem while the corresponding object
        was also modified in the database.  Other forms of conflicts
        are possible, e.g. a file added while an object was added in
        the corresponding place, or inconsistent labeling of the
        filesystem objects (e.g. an existing file marked as removed,
        or a non-existing file marked as added).
        """
        return self.conflicts

    def conflict(self, fspath):
        """Helper to report a conflict.

        Conflicts can be retrieved by calling `errors()`.
        """
        if self.raise_on_conflicts:
            raise SynchronizationError(fspath)
        if fspath not in self.conflicts:
            self.conflicts.append(fspath)

    def check(self, container, name, fspath):
        """Compare an object or object tree from the filesystem.

        If the originals on the filesystem are not uptodate, errors
        are reported by calling `conflict()`.

        Invalid object names are reported by raising
        ``SynchronizationError``.
        """
        self.context = container
        if invalidName(name):
            raise SynchronizationError("invalid separator in name %r" % name)

        if not name:
            self.checkDirectory(container, fspath)
        else:
            key = originalKey(fspath, name, self.metadata)
            try:
                traverseKey(container, key)
            except:
                self.checkNew(fspath)
            else:
                self.checkOld(container, key, fspath)

            # Now check extra and annotations
            try:
                obj = traverseKey(container, key)
            except:
                pass
            else:
                adapter = self.getSynchronizer(obj)
                extras = adapter.extras()
                extrapath = fsutil.getextra(fspath)
                if extras and self.repository.exists(extrapath):
                    self.checkSpecials(extras, extrapath)

                annotations = adapter.annotations()
                annpath = fsutil.getannotations(fspath)
                if annotations and self.repository.exists(annpath):
                    self.checkSpecials(annotations, annpath)

    def checkSpecials(self, container, fspath):
        """Helper to check a directory."""

        nameset = {}
        for key in container:
            nameset[key] = 1
        for name in self.metadata.getnames(fspath):
            nameset[name] = 1
        # Sort the list of keys for repeatability
        names = nameset.keys()
        names.sort()
        for name in names:
            self.check(container, name, self.repository.join(fspath, name))


    def checkDirectory(self, container, fspath):
        """Helper to check a directory."""
        adapter = self.getSynchronizer(container)
        nameset = {}
        if interfaces.IDirectorySynchronizer.providedBy(adapter):
            for key, obj in adapter.iteritems():
                nameset[key] = 1
        else:
            for key in container:
                nameset[key] = 1
        for name in self.metadata.getnames(fspath):
            nameset[name] = 1
        # Sort the list of keys for repeatability
        names = nameset.keys()
        names.sort()
        for name in names:
            self.check(container, name, self.repository.join(fspath, name))

    def checkNew(self, fspath):
        """Helper to check a new object."""
        entry = self.metadata.getentry(fspath)
        if entry:
            if entry.get("flag") != "added":
                self.conflict(fspath)
            else:
                if not self.repository.exists(fspath):
                    self.conflict(fspath)
            if self.repository.isdir(fspath):
                # Recursively check registered contents
                for name in self.metadata.getnames(fspath):
                    self.checkNew(self.repository.join(fspath, name))

    def checkOld(self, container, name, fspath):
        """Helper to check an existing object."""
        entry = self.metadata.getentry(fspath)
        if not entry:
            self.conflict(fspath)
        if "conflict" in entry:
            self.conflict(fspath)
        flag = entry.get("flag")
        if flag == "removed":
            if self.repository.exists(fspath):
                self.conflict(fspath)
        else:
            if not self.repository.exists(fspath):
                self.conflict(fspath)

        key = originalKey(fspath, name, self.metadata)
        obj = traverseKey(container, key)
        adapter = self.getSynchronizer(obj)
        if interfaces.IDirectorySynchronizer.providedBy(adapter):
            if flag != "removed" or self.repository.exists(fspath):
                self.checkDirectory(obj, fspath)
        else:
            if flag == "added":
                self.conflict(fspath)
            oldfspath = fsutil.getoriginal(fspath)
            if self.repository.exists(oldfspath):
                cmppath = oldfspath
            else:
                cmppath = fspath

            fp = self.repository.readable(cmppath)
            if not compare(fp, adapter):
                self.conflict(fspath)
            fp.close()


def getEntryId(obj):
    """Shortcut for adapter lookup."""
    return zope.component.queryAdapter(obj, interfaces.IEntryId)

def invalidName(name):
    return (os.sep in name or
            (os.altsep and os.altsep in name) or
            name == "." or
            name == ".." or
            "/" in name)

def traverseKey(container, key):
    return container[key]

def typeIdentifier(obj):
    return synchronizer.dottedname(obj.__class__)

def originalKey(fspath, name, metadata):
    """Reconstructs the original key from the metadata database."""
    entry = metadata.getentry(fspath)
    keytype = entry.get('keytype')
    key = entry.get('key', name)
    if keytype:
        keytype = resolveDottedname(keytype)
        if keytype == key.__class__:
            return key
        if keytype == unicode:
            return unicode(name, encoding='utf-8')
        return keytype(name)
    return name

def resolveDottedname(dottedname):
    factory = zope.dottedname.resolve.resolve(dottedname)
    if factory == eval:
        raise TypeError('invalid factory type')
    return factory


def compare(readable, dumper):
    """Help function for the comparison of a readable and a synchronizer.

    Simulates a writeable that raises an exception if the serializer
    dumps data which do not match the content of the readable.
    """
    class Failed(Exception):
        pass
    class Comparable(object):
        def write(self, data):
            echo = readable.read(len(data))
            if echo != data:
                raise Failed
    try:
        comparable = Comparable()
        dumper.dump(comparable)
        return readable.read() == ''
    except Failed:
        return False


class ComparePickles(object):

    def __init__(self, context, pickler):
        self.context = context
        self.pickler = pickler

    def dump(self, writeable):
        self.pickler.dump(self.context, writeable)
