# Copyright 2008, Holger Krekel. Licensed under GPL V3.
"""
module for reading and modifying the vadm.session sessionigfile
"""
from __future__ import generators

import py

# property for storing posix owner/group/permission information
vadmpropname = 'vadm:posix'

def update_hostwc(session):
    """ update the hostwc (and ensure that all neccessary working-copies are there).
    """
    if not session.hostwc.check() or \
        not session.hostwc.localpath.join('.svn').check(dir=1):
        raise SystemExit, "no valid working copy found at: %s.  Checkout one?" % str(session.hostwc)

    session.log.debug("checking status of %s" % session.hostwc)
    s = session.hostwc.status(rec=1, updates=1)
    if s.update_available:
        print 'performing neccessary local update on hostrepo.'
        session.hostwc.revert(rec=1)
        session.hostwc.update()
        
def getposix(localpath):
    """ return owner/group/perm encoded in a string. """
    localpath = py.path.local(localpath)
    l = []
    stat = localpath.stat()
    try: owner = stat.owner
    except KeyError: owner = str(stat.uid)
    try: group = stat.group
    except KeyError: group = str(stat.gid)
    l.extend([owner, group, oct(stat.mode)])
    value = " ".join(l)
    return value


def wc2fs(wcpath, localpath):
    """ tranfer one svn-working copy item to the filesystem. """
    assert localpath.check(link=0), "cannot handle links yet"

    posix = wcpath.propget(vadmpropname).strip().split()
    user,group,mode = posix
    mode = oct(int(mode, base=8) & 077777)

    source = wcpath.strpath
    target = str(localpath)
    if wcpath.check(file=1):
        tmp = target + '__vadmtmp'
        sh = ("cp %(source)r %(tmp)r;"
              "chown %(user)s:%(group)s %(tmp)r;"
              "chmod %(mode)s %(tmp)r;"
              "mv %(tmp)r %(target)r;"
              "chmod %(mode)s %(target)r;"
              ) % locals()
    else:
        sh = ("chown %(user)s:%(group)s %(target)r;"
              "chmod %(mode)s %(target)r;") % locals()
    #print "execing via sudo: ", sh
    py.process.cmdexec("sudo sh -c '%s'" % sh)


def content_fs2wc(session, target, wcpath):
    """ copy the local file 'target' to its working-copy equivalent. """
    try:
        f = target.open('rb')
        content = f.read()
        f.close()
        f = wcpath.open('wb')
        f.write(content)
        f.close()
    except py.error.EACCES, e:
        session.log.debug('permission denied on %s, trying sudo' % target)
        py.process.cmdexec("sudo sh -c 'cp \"%s\" \"%s\"'" % (target, wcpath))

def posix_fs2wc(session, target, wcpath):
    """ copy 'target's posix information to the working-copy item. """
    value = getposix(target)
    wcpath.propset(vadmpropname, value)

def all_fs2wc(session):
    result = session.hostwc.proplist(rec=1).items()
    pending_propsets = {}

    for wcpath, propdict in result:
        if  vadmpropname in propdict:
            target = wcpath.relto(session.hostwc)
            target = session.systemroot.join(target)
            try:
                value = getposix(target)
            except py.error.ENOENT:
                session.log.debug('file %r not found, skipping' % str(target))
                continue
            except OSError:
                session.log.warn('no posix info for %r, skipping' % str(target))
                continue

            pending_propsets.setdefault(value, []).append(wcpath)
            if not target.check(dir=1):
                content_fs2wc(session, target, wcpath)
    
    for value, wcpathlist in pending_propsets.items():
        fnames = [str(wc.localpath) for wc in wcpathlist[1:]]
        wcpathlist[0].propset(vadmpropname, value, *fnames)
