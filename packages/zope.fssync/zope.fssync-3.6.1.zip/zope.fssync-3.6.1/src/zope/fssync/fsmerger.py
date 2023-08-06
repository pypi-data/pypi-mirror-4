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
"""Higher-level three-way file and directory merger.

$Id: fsmerger.py 117584 2010-10-15 22:05:51Z patricks $
"""

import os
import shutil

from os.path import basename, dirname, exists, isfile, isdir, join, normcase

from zope.xmlpickle import dumps

from zope.fssync.merger import Merger
from zope.fssync import fsutil

class FSMerger(object):

    """Higher-level three-way file and directory merger.

    If overwrite_local is True, then local should be replaced with
    the remote, regardless of local changes.
    """

    def __init__(self, metadata, reporter, overwrite_local=False):
        """Constructor.

        Arguments are a metadata database and a reporting function.
        """
        self.metadata = metadata
        self.reporter = reporter
        self.merger = Merger(metadata)
        self.overwrite_local = overwrite_local

    def merge(self, local, remote):
        """Merge remote file or directory into local file or directory."""
        if ((isfile(local) or not exists(local))
            and
            (isfile(remote) or not exists(remote))):
            self.merge_files(local, remote)
        elif ((isdir(local) or not exists(local))
              and
              (isdir(remote) or not exists(remote))):
            self.merge_dirs(local, remote)
        else:
            # One is a file, the other is a directory.
            if self.local_modifications(local):
                # We have local modifications, so we cannot replace
                # the local object without loss.
                # SVN reports a failure here and so do we 
                self.reporter("C %s" % local)
                return
                # Since this is more
                # like a conflict that should be resolved one could
                # also make a backup and report a warning.
                
                # self.backup(local)
                # self.reporter("B %s" % local)
            else:
                # If we have no local modifications we
                # simply replace the local object with it's
                # remote counterpart.
                self.remove(local)
            self.merge(local, remote)
            return
        flag = self.metadata.getentry(local).get("flag")
        self.merge_extra(local, remote, flag)
        self.merge_annotations(local, remote, flag)
        if not exists(local) and not self.metadata.getentry(local):
            self.remove_special(local, "Extra")
            self.remove_special(local, "Annotations")
            self.remove_special(local, "Original")

    def local_modifications(self, local):
        """Helper to check for local modifications."""
        lentry = self.metadata.getentry(local)
        flag = lentry.get("flag")
        if flag == 'added':
            return True
        if isdir(local):
            locals = [join(local, name)
                           for name in os.listdir(local)]
            for path in locals:
                if self.local_modifications(path):
                    return True
            return False
        else:
            original = fsutil.getoriginal(local)
            if not exists(original):
                return True
            return not self.merger.cmpfile(local, original)

    def backup(self, local):
        """Helper to preserve unmergeable local files."""
        appendix = '.OLD'
        target = local + appendix
        count = 0
        while exists(target):
            count += 1
            target = "%s%s%s" % (local, appendix, count)
        shutil.move(local, target)

    def remove(self, local):
        """Helper to remove a local file or directory."""
        if isdir(local):
            try:
                shutil.rmtree(local)
                self.reportdir("D", local)
            except os.error:
                self.reportdir("?", local)
        else:
            try:
                os.remove(local)
                self.remove_special(local, "Original")
                self.reporter("D %s" % local)
            except:
                self.reporter("? %s" % local)

    def merge_extra(self, local, remote, flag):
        """Helper to merge the Extra trees."""
        lextra = fsutil.getextra(local)
        rextra = fsutil.getextra(remote)
        self.merge_dirs(lextra, rextra, flag=flag, special=True)

    def merge_annotations(self, local, remote, flag):
        """Helper to merge the Anotations trees."""
        lannotations = fsutil.getannotations(local)
        rannotations = fsutil.getannotations(remote)
        self.merge_dirs(lannotations, rannotations, flag=flag, special=True)

    def remove_special(self, local, what):
        """Helper to remove an Original, Extra or Annotations file/tree."""
        target = fsutil.getspecial(local, what)
        dir = dirname(target)
        if exists(target):
            if isdir(target):
                shutil.rmtree(target)
            else:
                # When should this ever happen?
                os.remove(target)
        # remove the specials directory only if it's empty
        if isdir(dir):
            try:
                os.rmdir(dir)
            except os.error:
                pass

    def merge_files(self, local, remote):
        """Merge remote file into local file."""
        # Reset sticky conflict if file was removed
        entry = self.metadata.getentry(local)
        conflict = entry.get("conflict")
        if conflict and not os.path.exists(local):
            del entry["conflict"]

        original = fsutil.getoriginal(local)
        action, state = self.merger.classify_files(local, original, remote)
        if action == 'Merge' and state == 'Modified' and self.overwrite_local:
            action = 'Copy'
            state = 'Uptodate'
        state = self.merger.merge_files(local, original, remote,
                                        action, state) or state
        self.reportaction(action, state, local)

    def merge_dirs(self, localdir, remotedir, flag=None, special=False):
        """Merge remote directory into local directory."""
        
        #uo: How do we handle unicode filenames?
         
        lentrynames = self.metadata.getnames(localdir)
        rentrynames = self.metadata.getnames(remotedir)
        lentry = self.metadata.getentry(localdir)
        rentry = self.metadata.getentry(remotedir)
                
        if not lentrynames and not rentrynames:

            if not lentry:
                if not rentry:
                    if exists(localdir) and not special:
                        self.reportdir("?", localdir)
                else:
                    if not exists(localdir):
                        self.make_dir(localdir)
                        lentry.update(rentry)
                        self.reportdir("N", localdir)
                    else:
                        # call make_dir() to create @@Zope and store metadata
                        self.make_dir(localdir)
                        self.reportdir("*", localdir)
                return

            if lentry.get("flag") == "added":
                if not rentry:
                    self.reportdir("A", localdir)
                else:
                    self.reportdir("U", localdir)
                    del lentry["flag"]
                return

            if lentry.get("flag") == "removed":
                if rentry:
                    self.reportdir("R", localdir)
                else:
                    self.reportdir("D", localdir)
                    lentry.clear()
                return

            if not rentry:
                self.clear_dir(localdir)
                return

        if not special:
            flag = lentry.get("flag")
        if exists(localdir):
            if flag == "added":
                if exists(remotedir):
                    self.reportdir("U", localdir)
                    if "flag" in lentry:
                        del lentry["flag"]
                else:
                    self.reportdir("A", localdir)
            else:
                if rentry or exists(remotedir):
                    self.reportdir("/", localdir)
                else:
                    # Tree removed remotely, must recurse down locally
                    for name in lentrynames:
                        # merge() removes the local copies since the
                        # remote versions are gone, unless there have
                        # been local changes.
                        self.merge(join(localdir, name), join(remotedir, name))
                    if flag != "added":
                        self.clear_dir(localdir)
                    return

            lnames = dict([(normcase(name), name)
                           for name in os.listdir(localdir)])
        else:
            if flag == "removed":
                self.reportdir("R", localdir)
                return # There's no point in recursing down!
            if rentry or rentrynames:
                # remote directory is new
                self.make_dir(localdir)
                lentry.update(rentry)
                self.reportdir("N", localdir)
            lnames = {}

        for name in lentrynames:
            lnames[normcase(name)] = name

        if exists(remotedir):
            rnames = dict([(normcase(name), name)
                           for name in os.listdir(remotedir)])
        else:
            rnames = {}

        for name in rentrynames:
            rnames[normcase(name)] = name

        names = {}
        names.update(lnames)
        names.update(rnames)
        if fsutil.nczope in names:
            del names[fsutil.nczope]

        # TODO: We must find a better way to avoid
        # the problem that unicode paths and str paths occur together
        # in the names dict
        
        for k, v in names.items():
            if not isinstance(k, unicode):
                del names[k]
                k = unicode(k, encoding='utf-8')
                if not isinstance(v, unicode):
                    v = unicode(v, encoding='utf-8')
                names[k] = v
                
        ncnames = sorted(names.keys())
        for ncname in ncnames:
            name = names[ncname]
            self.merge(join(localdir, name), join(remotedir, name))

    def make_dir(self, localdir):
        """Helper to create a local directory.

        This also creates the @@Zope subdirectory and places an empty
        Entries.xml file in it.
        """
        fsutil.ensuredir(localdir)
        localzopedir = join(localdir, "@@Zope")
        fsutil.ensuredir(localzopedir)
        efile = join(localzopedir, "Entries.xml")
        if not os.path.exists(efile):
            data = dumps({})
            f = open(efile, "w")
            try:
                f.write(data)
            finally:
                f.close()

    def clear_dir(self, localdir):
        """Helper to get rid of a local directory.

        This zaps the directory's @@Zope subdirectory, but not other
        files/directories that might still exist.

        It doesn't deal with extras and annotations for the directory
        itself, though.
        """
        lentry = self.metadata.getentry(localdir)
        lentry.clear()
        localzopedir = join(localdir, "@@Zope")
        if os.path.isdir(localzopedir):
            shutil.rmtree(localzopedir)
        try:
            os.rmdir(localdir)
        except os.error:
            self.reportdir("?", localdir)
        else:
            self.reportdir("D", localdir)

    def reportdir(self, letter, localdir):
        """Helper to report something for a directory.

        This adds a separator (e.g. '/') to the end of the pathname to
        signal that it is a directory.
        """
        if letter == "?" and self.ignore(localdir):
            letter = "*"
        self.reporter("%s %s" % (letter, join(localdir, "")))

    def reportaction(self, action, state, local):
        """Helper to report an action and a resulting state.

        This always results in exactly one line being reported.
        Report letters are:

        C -- conflicting changes not resolved (not committed)
        U -- file brought up to date (possibly created)
        M -- modified (not committed)
        A -- added (not committed)
        R -- removed (not committed)
        D -- file deleted
        ? -- file exists locally but not remotely
        * -- nothing happened
        """
        assert action in ('Fix', 'Copy', 'Merge', 'Delete', 'Nothing'), action
        assert state in ('Conflict', 'Uptodate', 'Modified', 'Spurious',
                         'Added', 'Removed', 'Nonexistent'), state
        letter = "*"
        if state == "Conflict":
            letter = "C"
        elif state == "Uptodate":
            if action in ("Copy", "Fix", "Merge"):
                letter = "U"
        elif state == "Modified":
            letter = "M"
        elif state == "Added":
            letter = "A"
        elif state == "Removed":
            letter = "R"
        elif state == "Spurious":
            if not self.ignore(local):
                letter = "?"
        elif state == "Nonexistent":
            if action == "Delete":
                letter = "D"
        self.reporter("%s %s" % (letter, local))

    def ignore(self, path):
        # TODO: This should have a larger set of default patterns to
        # ignore, and honor .cvsignore
        fn = basename(path)
        return (fn.endswith("~")

                # CVS crud (retrieved older versions):
                or fn.startswith(".#")

                # special names from various revision control systems:
                or fn in (".cvsignore", "CVS", "RCS", "SCCS", ".svn"))
