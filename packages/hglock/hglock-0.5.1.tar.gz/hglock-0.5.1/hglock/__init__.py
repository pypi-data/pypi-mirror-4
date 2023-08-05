# cooperative file locking extension
#
# Copyright 2011 aragost Trifork
#
# This software may be used and distributed according to the terms of
# the GNU General Public License version 2 or any later version.

"""cooperative file locking

When working with files that cannot be merged easily, such as Word
documents or Photoshop images, upfront communication is needed to make
sure that only one persons works on a given file at a time. If
parallel versions are created by accident, then work is either lost,
or a cumbersome hand-merge must be made.

This extension is a tool to help with the communication. It is assumed
that everybody has access to a central repository that will function
as the *lock repository*. The lock repository stores information about
which files are locked and by whom. That way, users can easily see
what the other members of their team is working on (with :hg:`locks`).
The lock repository must be initialized with :hg:`init-lock` before
use and clients use :hg:`lock` and :hg:`push` to lock/unlock files
(pushing unlocks the files touched by the pushed changesets). There is
also a :hg:`unlock` command, but it can only be used to unlock a file
that has not been modified locally, to prevent parallel work.

When it is known that a certain file type cannot be merged, it is
convenient to always require a lock when editing it. The extension
will read a ``.hglocks`` file in the root of the repository. This file
has the same syntax as a ``.hgignore`` file. Locking is mandatory for
files matches by ``.hglocks``.

When locking is mandatory for a file, :hg:`commit` will *ignore*
changes to the file unless it is locked. This supports the scenario
where you work with a set of binary files (say chapters in a book, all
of which change when page numbers are updated) but only wish to commit
some of them (the chapters where you actually changed the content).

The lock repository will also require you to lock files matched by
``.hglocks`` before you can push changesets that touch them.
"""

# The updatewriteperms feature is still experimental, so we don't
# advertise it in the docstring:

# Finally, files with mandatory locking can be marked read-only in the
# working copy until you lock them. To enable this behavior, set::
# 
#     [hglock]
#     updatewriteperm = True
# 
# in a configuration file. After that, when a repository is cloned,
# files marked as needing locking (those matched by ``.hglocks``) will
# be checked out read-only. After a file is locked, the file will be
# made writable. When unlocked (with via :hg:`unlock` or :hg:`push`),
# the file will be read-only again.

__version__ = '0.5.1'

import os, errno, time, socket, email.Utils, email.Generator, cStringIO, stat

from mercurial import hg, util, cmdutil, pushkey, extensions, ignore
from mercurial import commands as hgcmds, encoding, node, error, mail
from mercurial import merge, filemerge, match as matchmod
from mercurial.i18n import _

# Careful imports to keep compatibility with Mercurial 1.8.x and 1.9.x
if hasattr(cmdutil, 'match'):
    match = cmdutil.match
else:
    # Running Mercurial 1.9.x. Create a 1.8.x compatible match
    # function.
    from mercurial import scmutil
    def match(repo, *args, **kwargs):
        return scmutil.match(repo[None], *args, **kwargs)

import pushkeyrpc
from unrepr import unrepr

#### Utility functions ####

def get_lockrepo(repo):
    """Return a lockrepo class.

    The lockrepo class will extend the passed repo object.
    """
    class lockrepo(repo.__class__):
        _hide_unlocked = False
        _lockaddr = None
        _locks = None
        _hglocks = None

        def _readlockdata(self, ctx):
            self.ui.debug("lock: reading lock data from %s\n" % ctx)
            self._lockaddr = findaddr(self.ui)
            self._hglocks = readhglocks(self, ctx)
            try:
                remote = remoterepo(self.ui, self, {})
                self._locks = Locks(remote)
            except LockError, inst:
                self.ui.note("warning: %s\n(%s)\n" % (inst, inst.hint))
                self._locks = {}

        def status(self, *args, **kwargs):
            changes = super(lockrepo, self).status(*args, **kwargs)
            if not self._hide_unlocked:
                return changes
            self.ui.debug('lock: will hide unlocked modified files\n')
            try:
                remote = remoterepo(self.ui, self, {})
                locks = Locks(remote)
            except LockError, inst:
                self.ui.note("warning: %s\n(%s)\n" % (inst, inst.hint))
                return changes

            addr = findaddr(self.ui)
            ctx = self['.']
            date = int(time.time())
            branch = ctx.branch()
            match = kwargs.get('match')
            if not match:
                match = matchmod.always(self.root, self.getcwd())
            hglocks = readhglocks(self, repo[None])

            # we are only interested in modified and removed
            # files, not added files
            for status in changes[0], changes[2]:
                filtered = []
                for path in status:
                    mustlock = hglocks(path)
                    islocked = (branch, path) in locks
                    if islocked:
                        # update lock timestamp
                        errmsg = setremotelock(self.ui, remote, self, ctx,
                                               branch, path,
                                               addr, date)
                        if errmsg:
                            report(self.ui, match, path,
                                   "%s: %s" % (path, errmsg))
                        else:
                            self.ui.note(_("updated lock timestamp for %s\n")
                                         % path)
                            filtered.append(path)
                    else:
                        # not locked
                        if mustlock:
                            report(self.ui, match, path,
                                   _("%s: file has been modified without "
                                     "being locked, while locking is "
                                     "mandatory for this file") % path,
                                   hint=_("to commit the file, revert "
                                          "and then lock it"))
                        else:
                            filtered.append(path)

                status[:] = filtered
            return changes

        def commit(self, *args, **kwargs):
            # flip status switch if we're not committing a merge
            merging = (len(self.parents()) == 2)
            self._hide_unlocked = not merging
            try:
                return super(lockrepo, self).commit(*args, **kwargs)
            finally:
                self._hide_unlocked = False

        def addchangegroup(self, *args, **kwargs):
            clstart = len(self.changelog)
            try:
                return super(lockrepo, self).addchangegroup(*args, **kwargs)
            finally:
                clend = len(self.changelog)
                if clend > clstart:
                    releaselocks(repo, xrange(clstart, clend))

        def wwrite(self, filename, data, flags):
            super(lockrepo, self).wwrite(filename, data, flags)
            if not updatewriteperm(self.ui):
                return

            if self._hglocks is None:
                self._readlockdata(repo[None])

            if self._hglocks(filename):
                key = (self.dirstate.branch(), filename)
                lock = self._locks.get(key)
                if lock is None or lock[0] != self._lockaddr:
                    makereadonly(self, filename)
                    # Set the lock for filename so that it wouldn't get locked
                    # again. Otherwise the file will get locked during a clone
                    # and again during the following update operation.
                    branch = self.dirstate.branch()
                    addr = findaddr(self.ui)
                    ctx = repo['tip']
                    fctx = ctx[filename]
                    latestctxhex = repo[fctx.linkrev()].hex()
                    self._locks.set(branch, filename, addr, latestctxhex,
                            ctx.hex(), int(time.time()), validate=False)
    return lockrepo


def report(ui, match, path, errmsg, hint=""):
    if path in match.files():
        # explicit match
        raise util.Abort(errmsg, hint=hint)
    else:
        # implicit match
        if hint:
            hint = " (%s)" % hint
        ui.warn(_('%s, modifications ignored%s\n') % (errmsg, hint))

def findaddr(ui):
    user = ui.config('email', 'from') or ui.username()
    name, addr = email.Utils.parseaddr(user)
    if not addr:
        raise util.Abort(_('found no email address in %r') % user,
                         hint=_('configure ui.username or email.from'))
    return addr

def updatewriteperm(ui):
    return ui.configbool('hglock', 'updatewriteperm')

def makewritable(repo, path):
    repo.ui.debug("lock: making %s writable\n" % path)
    path = repo.wjoin(path)
    mode = os.stat(path).st_mode
    os.chmod(path, (mode | 0666) & ~util.umask)

def makereadonly(repo, path):
    repo.ui.debug("lock: making %s read-only\n" % path)
    path = repo.wjoin(path)
    mode = os.stat(path).st_mode
    os.chmod(path, mode & ~(stat.S_IWUSR | stat.S_IWGRP | stat.S_IWOTH))

class LockError(util.Abort):
    pass

class NoLockRepo(LockError):
    def __init__(self):
        LockError.__init__(self, _('no lock repository configured'),
                           hint=_("to use the lock extension you must set "
                                  "up a repository as a lock repository and "
                                  "set paths.default-lock or paths.default "
                                  "to point to it"))

class MustInitLockRepo(LockError):
    def __init__(self, path):
        LockError.__init__(self, _('%s is not a lock repository') % path,
                           hint=_("to use the lock extension you must "
                                  "enable it in this repository"))


def remoterepo(ui, repo, opts):
    path = ui.expandpath('default-lock', 'default')
    if path == 'default-lock':
        raise NoLockRepo()
    try:
        # hg <= 2.2
        repo = hg.repository(hg.remoteui(repo, opts), path)
    except util.Abort:
        # hg >= 2.3
        repo = hg._peerorrepo(hg.remoteui(repo, opts), path)
    return repo

def age(timestamp):
    periods = [(_('y'), 365 * 24 * 60 * 60),
               (_('w'),   7 * 24 * 60 * 60),
               (_('d'),       24 * 60 * 60),
               (_('h'),            60 * 60),
               (_('m'),                 60),
               (_('s'),                  1)]

    now = time.time()
    diff = int(now - timestamp)

    result = ""
    if diff < 0:
        result = "-"
        diff = -diff

    for i, (unit, period) in enumerate(periods):
        if diff >= period:
            result += '%d%s' % (diff // period, unit)
            if i + 1 < len(periods):
                diff = diff % period
                unit, period = periods[i+1]
                result += '%02d%s' % (diff // period, unit)
            return result

    return _("now")

def readhglocks(repo, ctx):
    path = repo.wjoin('.hglocks')
    repo.ui.debug("lock: reading %s@%s\n" % (path, ctx))

    # Simplified version of ignore.ignore
    try:
        data = ctx[".hglocks"].data()
        pats, warnings = ignore.ignorepats(data.splitlines())
        for warning in warnings:
            repo.ui.warn("%s: %s\n" % (path, warning))
    except (error.LookupError, IOError):
        return util.never

    try:
        return matchmod.match(repo.root, '', [], pats)
    except util.Abort, inst:
        # Re-raise an exception where the src is the right file
        raise util.Abort('%s: %s' % (path, inst[0]))

#### Lock class ####

class Locks(dict):
    def __init__(self, repo, emptyok=False):
        self.dirty = False
        if repo.local():
            repo.ui.debug("lock: reading locks from local %s\n" % repo.root)
            self.repo = repo
            try:
                lockfile = repo.opener('locks', 'r')
                for line in lockfile:
                    key, value = unrepr(line)
                    self[key] = value
                lockfile.close()
            except IOError, inst:
                if inst.errno != errno.ENOENT:
                    raise
                if emptyok:
                    self.dirty = True
                else:
                    raise MustInitLockRepo(repo.root)
        else:
            repo.ui.debug("lock: reading locks from remote %s\n" % repo.path)
            self.repo = None
            data = repo.listkeys('locks')
            # This extension always inserts the empty string as a key
            # in the data dictionary, so we can use this to detect if
            # a remote repository has the extension enabled.
            if '' not in data:
                raise MustInitLockRepo(repo.path)
            del data['']
            for key, value in data.iteritems():
                self[unrepr(key)] = unrepr(value)

    def notify(self, branch, path, owner, thief):
        root = os.path.basename(self.repo.root)
        fromaddr = mail.addressencode(self.repo.ui, thief)
        toaddr = mail.addressencode(self.repo.ui, owner)
        subject = "%s: Lock stolen on %s" % (root, path)
        body = ("A lock of yours was stolen by %s:\n\n"
                "Repository: %s\n"
                "Branch:     %s\n"
                "Path:       %s\n") % (thief, root, branch, path)
        now = time.time()
        msg = mail.mimeencode(self.repo.ui, body)
        msg['From'] = fromaddr
        msg['To'] = toaddr
        msg['Cc'] = fromaddr
        msg['Subject'] = mail.headencode(self.repo.ui, subject)
        msg['User-Agent'] = 'Mercurial-lock/%s' % util.version()
        msg['Message-Id'] = '<lock-%s.%s@%s>' % (node.hex(os.urandom(8)),
                                                 now, socket.getfqdn())
        msg['Date'] = email.Utils.formatdate(now, localtime=True)

        fp = cStringIO.StringIO()
        generator = email.Generator.Generator(fp, mangle_from_=False)
        generator.flatten(msg)
        try:
            sendmail = mail.connect(self.repo.ui)
            sendmail(thief, [owner, thief], fp.getvalue())
        except util.Abort, e:
            self.repo.ui.warn("warning: no mail sent: %s\n" % e)

    def _validate(self, branch, path, filehex, userctxhex, locking):
        try:
            # Lookup user's filectx first since this uses the oldest
            # revision number, and so the server might have this
            # changeset even though the user has made other changesets
            # since.
            self.repo.ui.debug("lock: looking for %s in %s\n"
                               % (node.short(node.bin(filehex)), self.repo.root))
            userfctx = self.repo[filehex]
            fctx = self.repo[branch][path]
            repoctx = self.repo[fctx.linkrev()]
            if repoctx != userfctx:
                # The user's fctx does not match our ctx. This can be
                # caused by a merge combining branches with identical
                # changes made to path. We detect this by checking
                # that the user's ctx is a descendent of our fctx.
                userctx = self.repo[userctxhex]
                if repoctx.ancestor(userctx) != repoctx:
                    if locking:
                        hint = _('pull and then lock it')
                    else:
                        hint = _('pull and then unlock it')
                    raise Exception(_('your revision %s is outdated, '
                                      'latest revision is %s\n(%s)')
                                    % (userctx, repoctx, hint))
        except (error.RepoLookupError, error.LookupError), inst:
            self.repo.ui.debug("lock: %s\n" % inst)
            if locking:
                hint = _('push before locking it, use the --force option to '
                         'recover a stolen lock')
            else:
                hint = _('push your changes and the files will be '
                         'automatically unlocked')
            raise Exception(_('your new revision %s is not in the '
                              'lock repository yet\n(%s)')
                            % (node.short(node.bin(filehex)), hint))

    def set(self, branch, path, addr, filehex, userctxhex, locktime,
            throw=True, validate=True):
        key = (branch, path)
        if key in self:
            lockaddr = self[key][0]
            if addr != lockaddr:
                if throw:
                    raise Exception(_('the file is locked by %s') % lockaddr)
                else:
                    self.notify(branch, path, lockaddr, addr)
        else:
            if validate:
                self._validate(branch, path, filehex, userctxhex, locking=True)

        self[key] = (addr, locktime)
        self.dirty = True

    def unset(self, branch, path, addr, filehex, userctxhex,
              throw=True, validate=True):
        key = (branch, path)
        if key not in self:
            raise Exception(_('not locked'))
        else:
            if validate:
                self._validate(branch, path, filehex, userctxhex, locking=False)
            lockaddr, locktime = self[key]
            if lockaddr != addr:
                if throw:
                    raise Exception(_('the file is locked by %s') % lockaddr)
                else:
                    self.notify(branch, path, lockaddr, addr)
            del self[key]
            self.dirty = True

    def write(self):
        if not self.repo:
            raise Exception(_('can only write locks to local repository'))
        if not self.dirty:
            return
        wlock = self.repo.wlock()
        try:
            lockfile = self.repo.opener('locks', 'w', atomictemp=True)
            for key, value in sorted(self.iteritems()):
                lockfile.write(repr((key, value)) + '\n')
            lockfile.close()
        finally:
            wlock.release()

#### pushkey commands ####

@pushkeyrpc.command
def setlock(repo, path, addr, branch, filehex, userctxhex, date,
            throw, validate):
    wlock = repo.wlock()
    try:
        locks = Locks(repo)
        locks.set(branch, path, addr, filehex, userctxhex, date,
                  throw, validate)
        locks.write()
    finally:
        wlock.release()

@pushkeyrpc.command
def clearlock(repo, path, addr, branch, filehex, userctxhex, throw, validate):
    wlock = repo.wlock()
    try:
        locks = Locks(repo)
        locks.unset(branch, path, addr, filehex, userctxhex, throw, validate)
        locks.write()
    finally:
        wlock.release()

def listlocks(repo):
    try:
        locks = Locks(repo)
    except MustInitLockRepo:
        # Return empty dictionary to signal the exception to the
        # client.
        return {}

    # Insert marker that will tell the client that the extension is
    # enabled. An empty dictionary is not enough: it could mean that
    # there are no locks or it could mean that the extension is not
    # enabled. The empty string is something that repr cannot return.
    data = {'': ''}
    for key, value in locks.iteritems():
        data[repr(key)] = repr(value)
    return data


def releaselocks(repo, revs):
    locks = Locks(repo, emptyok=True)
    hglocks = readhglocks(repo, repo[None])
    if not locks and hglocks == util.never:
        return

    wlock = repo.wlock()
    try:
        for rev in revs:
            ctx = repo[rev]
            branch = ctx.branch()
            name, addr = email.Utils.parseaddr(ctx.user())
            # addr might be empty here, but that will simply trigger
            # emails for all cleared locks in this changeset
            for f in ctx.files():
                key = (branch, f)
                if key in locks:
                    repo.ui.write('releasing lock on %s (changed in %s)\n'
                                  % (f, ctx))
                    locks.unset(branch, f, addr, None, None,
                                throw=False, validate=False)
        locks.write()
    finally:
        wlock.release()


#### Client-side Mercurial commands ####

def initlock(ui, repo, **opts):
    """initialize lock storage"""
    locks = Locks(repo, emptyok=True)
    locks.write()

def locks(ui, repo, **opts):
    """show locked files

    Display locked files on the current branch. Each locked file is
    shown with the user who locked it and the time the lock was last
    refreshed. A lock is refreshed when it is created and when a
    commit involving a locked file is made.
    """
    wantedbranches = opts.get('branch')
    if opts.get('all'):
        wantedbranches = repo.branchmap().keys()
    if not wantedbranches:
        wantedbranches = [repo.dirstate.branch()]
    remote = remoterepo(ui, repo, opts)
    locks = Locks(remote)
    for branch, path in sorted(locks):
        if branch in wantedbranches:
            addr, locktime = locks[branch, path]
            ui.write("%s%s %s%s %6s %s\n"
                     % (addr, ' ' * (16 - encoding.colwidth(addr)),
                        branch, ' ' * (8 - encoding.colwidth(branch)),
                        age(locktime), path))

def setremotelock(ui, remote, repo, ctx, branch, path, addr, date,
                  throw=True, validate=True):
    if not validate:
        latestctxhex = None
    else:
        fctx = ctx[path]
        latestctxhex = repo[fctx.linkrev()].hex()
    return setlock(ui, remote, path,
                   encoding.fromlocal(addr), encoding.fromlocal(branch),
                   latestctxhex, ctx.hex(), date, throw, validate)

def lock(ui, repo, path, *pats, **opts):
    """lock the specified files

    Lock the specified files in the lock repository. To lock a file,
    it must be unmodified and it must be up to date. Up to date means
    that there is no newer version of the file in the lock repository.

    Use the -f/--force flag to steal a lock held by someone else. This
    transfers the lock to another user. The old lock owner will be
    notified with an email when this happens. The --force flag can
    also be used to bypass the check for up to date files.

    Returns 0 if all files were succesfully locked, 1 otherwise.
    """
    exitcode = 0
    force = opts.get('force')
    addr = findaddr(ui)
    hglocks = readhglocks(repo, repo[None])
    remote = remoterepo(ui, repo, opts)
    branch = repo.dirstate.branch()
    date = int(time.time())

    # need both ctx and wctx since we cannot pass a workingctx to
    # setremotelock because is calls workingfilectx.linkrev, which
    # crashes as files in the working copy has no linkrev
    ctx = repo['.']
    wctx = repo[None]
    changed = set(wctx.added() + wctx.modified() +
                  wctx.removed() + wctx.deleted())

    oldlocks = Locks(remote)
    m = match(repo, (path,) + pats, opts)
    for path in repo.walk(m):
        hint = None
        if path in changed:
            errmsg = _('file has local changes')
            hint = _("revert the file and then lock it")
        elif path not in wctx:
            errmsg = _("no such file in revision %s") % ctx
            hint = _("add, commit, and push it before attempting to lock it")
        else:
            errmsg = setremotelock(ui, remote, repo, ctx, branch, path,
                                   addr, date,
                                   throw=not force, validate=not force)
        if errmsg:
            report(ui, m, path,
                   _('could not lock %s: %s') % (path, errmsg), hint)
            exitcode = 1
        else:
            lockaddr = oldlocks.get((branch, path), (None, 0))[0]
            if lockaddr and lockaddr != addr and force:
                ui.write(_("%s: lock has been stolen, notification "
                           "sent to %s\n") % (path, lockaddr))
            else:
                ui.note(_("locked %s\n") % path)
            if updatewriteperm(ui) and hglocks(path):
                makewritable(repo, path)
    return exitcode

def unsetremotelock(ui, remote, repo, ctx, branch, path, addr, throw, validate):
    if not validate:
        latestctxhex = None
    else:
        fctx = ctx[path]
        latestctxhex = repo[fctx.linkrev()].hex()
    return clearlock(ui, remote, path,
                     encoding.fromlocal(addr), encoding.fromlocal(branch),
                     latestctxhex, ctx.hex(), throw, validate)

def unlock(ui, repo, path, *pats, **opts):
    """unlock the specified files

    Remove the lock on the specified files from the lock repository.
    To unlock a file, it must be unmodified and it must be up to date.
    Up to date means that there is no newer version of the file in the
    lock repository.

    Use the -f/--force flag to break a lock by forcibly removing it
    from the lock repository. The old lock owner will be notified with
    an email when this happens. The --force flag can also be used to
    bypass the check for up to date files.

    Returns 0 if all files were succesfully unlocked, 1 otherwise.
    """
    exitcode = 0
    force = opts.get('force')
    addr = findaddr(ui)
    hglocks = readhglocks(repo, repo[None])
    remote = remoterepo(ui, repo, opts)
    branch = repo.dirstate.branch()

    oldlocks = Locks(remote)
    ctx = repo['.']
    wctx = repo[None]
    changed = set(wctx.added() + wctx.modified() +
                  wctx.removed() + wctx.deleted())
    m = match(repo, (path,) + pats, opts)
    for path in repo.walk(m):
        if (branch, path) not in oldlocks:
            ui.note(_("%s was not locked\n") % path)
            continue

        hint = None
        if path in changed:
            errmsg = _('file has local changes')
            hint = _("revert the file and then unlock it")
        elif path not in wctx:
            errmsg = _("no such file in revision %s") % repo['.']
            hint = _("add, commit, and push it before attempting to unlock it")
        else:
            errmsg = unsetremotelock(ui, remote, repo, ctx, branch, path,
                                     addr, throw=not force, validate=not force)
        if errmsg:
            report(ui, m, path,
                   _('could not unlock %s: %s') % (path, errmsg), hint)
            exitcode = 1
        else:
            lockaddr = oldlocks.get((branch, path), (None, 0))[0]
            if lockaddr and lockaddr != addr and force:
                ui.write(_("%s: file has been unlocked, notification "
                           "sent to %s\n") % (path, lockaddr))
            else:
                ui.note(_("unlocked %s\n") % path)
            if updatewriteperm(ui) and hglocks(path):
                makereadonly(repo, path)
    return exitcode

def checkpush(ui, repo, dest, opts):
    ui.pushbuffer()
    outgoing = hg._outgoing(ui, repo, dest, opts)
    ui.popbuffer()

    lockfiles = set() # files that we have modified or added with a lock

    if not outgoing:
        return lockfiles

    ui.debug('lock: checking %s\n' % ', '.join(map(node.short, outgoing)))

    remote = remoterepo(ui, repo, opts)
    try:
        locks = Locks(remote, emptyok=True)
    except LockError, inst:
        ui.note(_("warning: %s\n(%s)\n") % (inst, inst.hint))
        return lockfiles

    hglocks = readhglocks(repo, repo[None])
    if not locks and hglocks == util.never:
        return lockfiles

    badfiles = set() # files that we have modified or removed without a lock
    goodfiles = set() # files that we have added (no lock required)

    for o in outgoing:
        ctx = repo[o]
        branch = ctx.branch()
        name, addr = email.Utils.parseaddr(ctx.user())
        for f in ctx.files():
            if f in goodfiles:
                ui.debug("lock: %s is added, ignoring\n" % f)
                continue
            if util.all([f not in p for p in ctx.parents()]):
                ui.debug("lock: %s is added in %s, ignoring\n" % (f, ctx))
                goodfiles.add(f)
                renameinfo = ctx[f].renamed()
                if renameinfo:
                    # The file was renamed or copied. We add it to the
                    # list of lockfiles if the copy parent is a locked
                    # file or if the parent is a copy of another
                    # locked file.
                    parent = renameinfo[0]
                    if (branch, parent) in locks or parent in lockfiles:
                        lockfiles.add(f)
                continue

            key = (branch, f)
            if key in locks:
                lockowner = locks[key][0]
                ui.debug('lock: %s is locked by %s, modified by %s in %s\n'
                         % (f, lockowner, addr, ctx))
                if lockowner != addr:
                    badfiles.add(f)
                else:
                    lockfiles.add(f)
            else:
                ui.debug('lock: %s is not locked\n' % f)
                if hglocks(f):
                    # f should have been locked but isn't -- this can
                    # happen if Bob steals Alice's lock and unlocks
                    # the file after Alice made a local commit to it.
                    badfiles.add(f)
                    ui.debug('lock: %s should have been locked\n' % f)

    if badfiles:
        raise util.Abort(_("rejecting push because of unlocked files: %s")
                         % ", ".join(sorted(badfiles)),
                         hint=_("pull to get the latest versions of the files, "
                                "lock, merge your changes, push again"))
    return lockfiles

def push(orig, ui, repo, dest=None, **opts):
    if opts.get('force'):
        raise util.Abort(_("the lock extension does not allow pushing "
                           "new heads, even with the force option"),
                         hint=_("you must pull and merge, then push again"))
    try:
        lockfiles = checkpush(ui, repo, dest, opts)
        orig(ui, repo, dest, **opts)
    except util.Abort, inst:
        if inst.hint.endswith(_("use push -f to force")):
            inst.hint = _("you must pull and merge, then push again")
        raise inst

    if updatewriteperm(ui):
        # Now the files have been pushed successfully, so make them
        # read-only.
        for path in lockfiles:
            # Some of the paths might not exist because of renames or
            # deletions.
            if os.path.exists(repo.wjoin(path)):
                makereadonly(repo, path)
        return

def applyupdates(orig, repo, action, wctx, mctx, actx, overwrite):
    """Fix permissions on files after an update/merge.

    If changing to a rev where a lock is held, make the file writable.
    Likewise if changing to one where it is not held and requires a
    lock, this makes the file read-only.
    """
    # Make the wwrite method in lockrepo use the .hglocks file from
    # the revision we're updating to. This is especially important for
    # new clones where we update from the null revision to the tip and
    # we want files to be read-write and read-only based on the
    # .hglocks file in tip.
    lockrepo = get_lockrepo(repo)
    repo.__class__ = lockrepo
    repo._readlockdata(mctx)

    try:
        remote = remoterepo(repo.ui, repo, {})
        locks = Locks(remote)
    except LockError, inst:
        repo.ui.note(_("warning: %s\n(%s)\n") % (inst, inst.hint))
        return orig(repo, action, wctx, mctx, actx, overwrite)

    addr = findaddr(repo.ui)
    branch = mctx.branch() # target branch
    hglocks = readhglocks(repo, mctx) # .hglocks in target revision
    modified = wctx.modified()

    def picktool(orig, repo, ui, path, binary, symlink):
        if path in modified:
            key = (branch, path)
            if key in locks and locks[key][0] == addr:
                # we hold the lock -- the other messed up
                repo.ui.debug("%s is locked by us, but modified in remote\n"
                              % path)
                return ('internal:dump', None)
            if hglocks(path):
                # we should hold the lock, but don't -- we messed up
                repo.ui.debug("%s should have been locked by us\n" % path)
                repo.ui.write(_("merging %s (was unlocked, local version "
                                "saved as %s.orig)\n") % (path, path))
                util.copyfile(path, path + '.orig')
                return ('internal:other', None)
        return orig(repo, repo.ui, path, binary, symlink)

    oldpicktool = extensions.wrapfunction(filemerge, '_picktool', picktool)
    try:
        result = orig(repo, action, wctx, mctx, actx, overwrite)
    finally:
        filemerge._picktool = oldpicktool

    if not updatewriteperm(repo.ui):
        return result

    # Run through the current locks and fix permisssions as needed. We
    # iterate over the locks instead of mctx since there will be fewer
    # locks than files in mctx.
    for (lockbranch, path), (lockowner, timestamp) in locks.iteritems():
        if not hglocks(path) or lockowner != addr:
            continue

        if lockbranch == branch:
            # We own the lock for this, so it should be writable.
            makewritable(repo, path)
        elif path in mctx:
            # We have not lock for this file, to make sure to reset
            # permissions. Normally, lockrepo.wwrite will mark files
            # read-only, but if there are no changes made to the file
            # between wctx and mctx, then wwrite wont be called.
            makereadonly(repo, path)
    return result

def cmdutilcopy(orig, ui, repo, pats, opts, rename=False):
    try:
        remote = remoterepo(ui, repo, {})
        locks = Locks(remote)
    except LockError, inst:
        ui.note(_("warning: %s\n(%s)\n") % (inst, inst.hint))
        return orig(ui, repo, pats, opts, rename)

    addr = findaddr(ui)
    hglocks = readhglocks(repo, repo[None])
    branch = repo.dirstate.branch()
    date = int(time.time())
    ctx = repo['.']

    def lockcopies(orig, src, dst):
        wcsrc = src[len(repo.root) + 1:]
        wcdst = dst[len(repo.root) + 1:]

        if rename and hglocks(wcsrc) and (branch, wcsrc) not in locks:
            raise util.Abort(_("%s: must be locked before renaming") % wcsrc)

        if hglocks(wcdst):
            errmsg = setremotelock(ui, remote, repo, ctx, branch, wcdst,
                                   addr, date, throw=True, validate=False)
            if errmsg:
                raise util.Abort(_("could not lock %s: %s") % (wcdst, errmsg))

        return orig(src, dst)

    oldcopy = extensions.wrapfunction(util, 'copyfile', lockcopies)
    try:
        return orig(ui, repo, pats, opts, rename)
    finally:
        util.copyfile = oldcopy

#### Setup ####

def reposetup(ui, repo):
    if not repo.local():
        return

    pushkeyrpc.registercallbacks(repo)
    lockrepo = get_lockrepo(repo)
    repo.__class__ = lockrepo

# atomictemp.rename was renamed to atomictemp.close after 1.9. This
# class adds that behavior to earlier clients.
class atomictempfile(util.atomictempfile):
    def close(self):
        return self.rename()

def extsetup(ui):
    # Install the forward-compatible atomictempfile class if the
    # current util.atomictempfile class has the rename method.
    if getattr(util.atomictempfile, 'rename', None):
        util.atomictempfile = atomictempfile

    pushkeyrpc.init()
    pushkey.register('locks', pushkeyrpc.nullpush, listlocks)
    extensions.wrapcommand(hgcmds.table, 'push', push)
    extensions.wrapfunction(merge, 'applyupdates', applyupdates)
    extensions.wrapfunction(cmdutil, 'copy', cmdutilcopy)


cmdtable = {
    "init-lock":
        (initlock,
         [],
         _('hg init-lock')),
    "locks":
        (locks,
         [('b', 'branch', [],
           _('show only locks on a specific branch'), _('BRANCH')),
          ('a', 'all', None,
           _('show locks for all branches'))],
         _('hg locks [-a] [-b BRANCH]')),
    "lock":
        (lock,
         [('f', 'force', None, _('steal lock'))],
         _('hg lock [-f] FILE...')),
    "unlock":
        (unlock,
         [('f', 'force', None, _('steal lock'))],
         _('hg unlock [-f] FILE...')),
}

testedwith = '2.2 2.3'

buglink = 'https://bitbucket.org/lantiq/hglock/issues'

