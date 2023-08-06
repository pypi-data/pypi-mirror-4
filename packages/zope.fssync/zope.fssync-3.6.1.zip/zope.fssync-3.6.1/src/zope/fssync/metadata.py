##############################################################################
#
# Copyright (c) 2003 Zope Corporation and Contributors.
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
"""Class to maintain fssync metadata.

The metadata entry for something named /path/base, is kept in a file
/path/@@Zope/Entries.xml.  That file is (an XML pickle for) a dict
containing many entries.  The metadata entry for /path/base is stored
under the key 'base'.  The metadata entry is itself a dict.  An empty
entry is considered non-existent, and will be deleted upon flush.  If
no entries remain, the Entries.xml file will be removed.

$Id: metadata.py 117584 2010-10-15 22:05:51Z patricks $
"""

import os
import copy

from cStringIO import StringIO
from os.path import exists, isfile, split, join, realpath, normcase
from xml.sax import ContentHandler, parseString
from xml.sax.saxutils import quoteattr

import fsutil

case_insensitive = (normcase("ABC") == normcase("abc"))

class Metadata(object):

    def __init__(self):
        """Constructor."""
        self.cache = {} # Keyed by normcase(dirname(realpath(file)))
        self.originals = {} # Original copy as read from file

    def getnames(self, dir):
        """Return the names of known non-empty metadata entries, sorted."""
        entries = self.getmanager(dir).entries
        names = [name for name, entry in entries.iteritems() if entry]
        names.sort()
        return names

    def getentry(self, file):
        """Return the metadata entry for a given file (or directory).

        Modifying the dict that is returned will cause the changes to
        the metadata to be written out when flush() is called.  If
        there is no metadata entry for the file, return a new empty
        dict, modifications to which will also be flushed.
        """
        file = realpath(file)
        dir, base = split(file)
        return self.getmanager(dir).getentry(base)

    def gettypeinfo(self, path):
        entry = self.getentry(path)
        return entry.get("type"), entry.get("factory")

    def getmanager(self, dir):
        dir = realpath(dir)
        key = normcase(dir)
        if key not in self.cache:
            self.cache[key] = DirectoryManager(dir)
        return self.cache[key]

    def flush(self):
        errors = []
        for dirinfo in self.cache.itervalues():
            try:
                dirinfo.flush()
            except (IOError, OSError), err:
                errors.append(err)
        if errors:
            if len(errors) == 1:
                raise
            else:
                raise IOError(tuple(errors))

    def added(self):
        """Adds an 'added' flag to all metadata entries."""
        for dirinfo in self.cache.itervalues():
            for entry in dirinfo.entries.itervalues():
                entry["flag"] = "added"

class DirectoryManager(object):

    def __init__(self, dir):
        self.zdir = join(dir, "@@Zope")
        self.efile = join(self.zdir, "Entries.xml")
        if isfile(self.efile):
            self.entries = load_entries_path(self.efile)
        else:
            self.entries = {}
        self.originals = copy.deepcopy(self.entries)

    def ensure(self):
        """Dump the entries even if there's an empty set."""
        self._dump(self._get_live())

    def flush(self):
        """Dump the entries if different from the set stored on disk."""
        live = self._get_live()
        if live != self.originals:
            if exists(self.efile) or live:
                self._dump(live)
            self.originals = copy.deepcopy(live)

    def _get_live(self):
        """Retrieve the set of all 'live' entries."""
        live = {}
        for name, entry in self.entries.iteritems():
            if entry:
                live[name] = entry
        return live

    def _dump(self, live):
        """Write entries to disk."""
        data = dump_entries(live)
        if not exists(self.zdir):
            os.makedirs(self.zdir)
        f = open(self.efile, "wb")
        try:
            f.write(data)
        finally:
            f.close()

    def getentry(self, name):
        """Return a single named entry.

        If there's no matching entry, an empty entry is created.
        """
        name = fsutil.encode(name)
        if name in self.entries:
            return self.entries[name]
        if case_insensitive:
            # Look for a case-insensitive match -- expensive!
            # TODO: There's no test case for this code!
            nbase = normcase(name)
            matches = [b for b in self.entries if normcase(b) == nbase]
            if matches:
                if len(matches) > 1:
                    raise KeyError("multiple entries match %r" % nbase)
                return self.entries[matches[0]]
        # Create a new entry
        self.entries[name] = entry = {}
        return entry


def dump_entries(entries):
    sio = StringIO()
    sio.write("<?xml version='1.0' encoding='utf-8'?>\n")
    sio.write("<entries>\n")
    names = entries.keys()
    names.sort()
    for name in names:
        entry = entries[name]
        name = fsutil.encode(name, 'utf-8')
        sio.write("  <entry name=")
        sio.write(quoteattr(name))
        for k, v in entry.iteritems():
            if v is None:
                continue
            k = fsutil.encode(k, 'utf-8')
            v = fsutil.encode(v, 'utf-8')
            sio.write("\n         %s=%s" % (k, quoteattr(v)))
        sio.write("\n         />\n")
    sio.write("</entries>\n")
    return sio.getvalue()

def load_entries(text):
    ch = EntriesHandler()
    try:
        parseString(text, ch)
    except FoundXMLPickle:
        from zope.xmlpickle import loads
        return loads(text)
    else:
        return ch.entries


def load_entries_path(path):
    f = open(path, 'rb')
    try:
        return load_entries(f.read())
    finally:
        f.close()


class EntriesHandler(ContentHandler):
    def __init__(self):
        self.first = True
        self.stack = []
        self.entries = {}

    def startElement(self, name, attrs):
        if self.first:
            if name == "pickle":
                raise FoundXMLPickle()
            elif name != "entries":
                raise InvalidEntriesFile()
            else:
                self.first = False
        if name == "entry":
            if self.stack[-1] != "entries":
                raise InvalidEntriesFile("illegal element nesting")
            else:
                entryname = attrs.getValue("name")
                entryname = fsutil.encode(entryname)
                entry = {}
                for n in attrs.getNames():
                    if n != "name":
                        entry[n] = attrs.getValue(n)
                self.entries[entryname] = entry
        elif name == "entries":
            if self.stack:
                raise InvalidEntriesFile(
                    "<entries> must be the document element")
        else:
            raise InvalidEntriesFile("unknown element <%s>" % name)

        self.stack.append(name)

    def endElement(self, name):
        old = self.stack.pop()
        assert name == old, "%r != %r" % (name, old)

    def characters(self, data):
        if data.strip():
            raise InvalidEntriesFile(
                "arbitrary character data not supported: %r" % data.strip())


class FoundXMLPickle(Exception):
    """Raised by EntriesHandler when the document appears to be an XML
    pickle."""

class InvalidEntriesFile(Exception):
    """Raised by EntriesHandler when the document has an unsupposed
    document element."""
