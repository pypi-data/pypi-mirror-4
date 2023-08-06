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
"""Class to do augmented three-way merges.

This boils down to distinguishing an astonishing number of cases.

$Id: merger.py 76667 2007-06-13 15:24:10Z oestermeier $
"""

import os
import shutil
import filecmp
import commands

from os.path import exists, isfile, dirname
from zope.fssync import fsutil

class Merger(object):
    """Augmented three-way file merges.

    An augmented merge takes into account three files and two metadata
    entries.  The files are labeled local, original, and remote.  The
    metadata entries are for local and remote.  A remote metadata
    entry is either empty or non-empty.  Empty means the file does not
    exist remotely, non-empty means it does exist remotely.  We also
    have to take into account the possibility that the existence of
    the file belies what the entry declares.  A local metadata entry
    can have those states, and in addition, if non-empty, it can be
    flagged as added or removed.  Again, the existence of the file may
    bely what the entry claims.  The original file serves the obvious
    purpose.  Its existence, too, can be inconsistent with the state
    indicated by the metadata entries.

    To find the metadata entry for a file, we use an abstraction
    called the metadata database; for our purposes, all we need is
    that the metadata database supports a getentry() method which
    returns the metadata as a dict.  Changes to this dict will cause
    changes to the metadata.

    The purpose of the merge_files() method is to merging the remote
    changes into the local copy as the best it can, resolving
    inconsistencies if possible.  It should not raise an exception
    unless there are file/directory permission problems.  Its return
    value is an indicator of the final state.

    The classify_files() methods is a helper for merge_files(); it
    looks at all the evidence and decides what merge_files() should
    do, without actually touching any files or metadata.  Possible
    actions are:

    Fix      -- copy the remote copy to the local original, nothing else
    Copy     -- copy the remote copy over the local copy and original
    Merge    -- merge the remote copy into the local copy
                (this may cause merge conflicts when executed);
                copy the remote copy to the local original
    Delete   -- delete the local copy and original
    Nothing  -- do nothing

    The original file is made a copy of the remote file for actions
    Fix, Copy and Merge; it is deleted for action Delete; it is
    untouched for action Nothing.

    The classify_files() method should also indicate the final state
    of the local copy after the action is taken:

    Conflict    -- there is a conflict of some kind
    Uptodate    -- the local copy is the same as the remote copy
    Modified    -- the local copy is marked (to be) modified
    Added       -- the local copy is marked (to be) added
    Removed     -- the local copy is marked (to be) removed
    Spurious    -- there is an unregistered local file only
    Nonexistent -- there is nothing locally or remotely

    For Conflict, Added and Removed, the action will always be
    Nothing.  The difference between Removed and Nonexistent is that
    Nonexistent means the file doesn't exist remotely either, while
    Removed means that on the next commit the file should be removed
    from the remote store.  Similarly, Added means the file should be
    added remotely on the next commit, and Modified means that the
    file should be changed remotely to match the local copy at the
    next commit.

    Note that carrying out the Merge action can change the resulting
    state to become Conflict instead of Modified, if there are merge
    conflicts (which classify_files() can't detect without doing more
    work than reasonable).
    """

    def __init__(self, metadata):
        """Constructor.

        The argument is the metadata database, which has a single
        method: getentry(file) which returns a dict containing the
        metadata for that file.  Changes to this dict will be
        preserved when the database is written back (not by the Merger
        class).  To delete all metadata for a file, call the dict's
        clear() method.

        We pass in the metadata database rather than inheriting from
        it, in part because this makes testing with a Mock metadata
        database easier.
        """
        self.metadata = metadata

    def getentry(self, file):
        """Helper to abstract away the existence of self.metadata."""
        return self.metadata.getentry(file)

    def merge_files(self, local, original, remote, action, state):
        """Merge files.

        The action and state arguments correspond to the return value
        of classify_files().

        Return the state as returned by the second return value of
        classify_files().  This is either the argument state or
        recalculated based upon the effect of the action.
        """
        method = getattr(self, "merge_files_" + action.lower())
        return method(local, original, remote) or state

    def merge_files_nothing(self, local, original, remote):
        return None

    def merge_files_delete(self, local, original, remote):
        if isfile(local):
            os.remove(local)
        if isfile(original):
            os.remove(original)
        self.getentry(local).clear()
        return None

    def merge_files_copy(self, local, original, remote):
        try:
            shutil.copy(remote, local)
        except IOError, msg:
            import pdb; pdb.set_trace()
            
        fsutil.ensuredir(dirname(original))
        shutil.copy(remote, original)
        self.getentry(local).update(self.getentry(remote))
        self.clearflag(local)
        return None

    def merge_files_merge(self, local, original, remote):
        # TODO: This is platform dependent
        if exists(original):
            origfile = original
        else:
            origfile = "/dev/null"
        # commands.mkarg() is undocumented; maybe use fssync.quote()
        cmd = "diff3 -m -E %s %s %s" % (commands.mkarg(local),
                                        commands.mkarg(origfile),
                                        commands.mkarg(remote))
        pipe = os.popen(cmd, "r")
        output = pipe.read()
        sts = pipe.close()
        if output or not sts:
            f = open(local, "wb")
            try:
                f.write(output)
            finally:
                f.close()
        fsutil.ensuredir(dirname(original))
        shutil.copy(remote, original)
        self.getentry(local).update(self.getentry(remote))
        self.clearflag(local)
        if sts:
            self.getentry(local)["conflict"] = "yes"
            return "Conflict"
        else:
            return "Modified"

    def merge_files_fix(self, local, original, remote):
        fsutil.ensuredir(dirname(original))
        shutil.copy(remote, original)
        self.clearflag(local)
        self.getentry(local).update(self.getentry(remote))
        return None

    def clearflag(self, file):
        """Helper to clear the added/removed metadata flag."""
        metadata = self.getentry(file)
        if "flag" in metadata:
            del metadata["flag"]

    def classify_files(self, local, original, remote):
        """Classify file changes.

        Arguments are pathnames to the local, original, and remote
        copies.

        Return a pair of strings (action, state) where action is one
        of 'Fix', 'Copy', 'Merge', 'Delete' or 'Nothing', and state is
        one of 'Conflict', 'Uptodate', 'Modified', 'Added', 'Removed',
        'Spurious' or 'Nonexistent'.
        
        """
        
        lmeta = self.getentry(local)
        rmeta = self.getentry(remote)
                    
        # Special-case sticky conflict
        if "conflict" in lmeta:
            return ("Nothing", "Conflict")
        
        # Sort out cases involving additions or removals

        if not lmeta and not rmeta:
            if exists(local):
                return ("Nothing", "Spurious")
            else:
                # Why are we here?
                # classify_files() should not have been called in this case.
                return ("Nothing", "Nonexistent")

        if lmeta.get("flag") == "added":
            # Added locally
            if not rmeta:
                # Nothing remotely
                return ("Nothing", "Added")
            else:
                # Added remotely too!  Merge, unless trivial conflict
                if self.cmpfile(local, remote):
                    return ("Fix", "Uptodate")
                else:
                    # CVS would say "move local file out of the way"
                    if rmeta.get("binary") == "true" or lmeta.get("binary") == "true":
                        return ("Nothing", "Conflict")
                    else:
                        return ("Merge", "Modified")

        if rmeta and not lmeta:
            # Added remotely
            return ("Copy", "Uptodate")

        if lmeta.get("flag") == "removed":
            if not rmeta:
                # Removed remotely too
                return ("Delete", "Nonexistent")
            else:
                # Removed locally
                if self.cmpfile(original, remote):
                    return ("Nothing", "Removed")
                else:
                    return ("Nothing", "Conflict")

        if lmeta and not rmeta:
            assert lmeta.get("flag") is None
            # Removed remotely
            return ("Delete", "Nonexistent")

        if lmeta.get("flag") is None and not exists(local):
            # Lost locally
            if rmeta:
                return ("Copy", "Uptodate")
            else:
                return ("Delete", "Nonexistent")

        # Sort out cases involving simple changes to files

        if self.cmpfile(original, remote):
            # No remote changes; classify local changes
            if self.cmpfile(local, original):
                # No changes
                return ("Nothing", "Uptodate")
            else:
                # Only local changes
                return ("Nothing", "Modified")
        else:
            # Some remote changes; classify local changes
            if self.cmpfile(local, original):
                # Only remote changes
                return ("Copy", "Uptodate")
            else:
                if self.cmpfile(local, remote):
                    # We're lucky -- local and remote changes are the same
                    return ("Fix", "Uptodate")
                else:
                    # Changes on both sides, three-way merge needed
                    if rmeta.get("binary") == "true" or lmeta.get("binary") == "true":
                        return ("Nothing", "Conflict")
                    else:
                        return ("Merge", "Modified")

    def cmpfile(self, file1, file2):
        """Helper to compare two files.

        Return True iff the files both exist and are equal.
        """
        if not (isfile(file1) and isfile(file2)):
            return False
        return filecmp.cmp(file1, file2, shallow=False)
