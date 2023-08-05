#!/usr/bin/env python
# Copyright 2008, Holger Krekel. Licensed under GPL V3.
"""
module providing a cmdline interface to vadm

"""
from __future__ import generators
import py, vadm 
from vadm import logger
import os, sys
from inspect import isclass
import optparse, textwrap

def userconsumer(msg):
    """ print info for the interactive user. """
    print msg.strcontent()

class Session:
    def __init__(self, hostwc=None, systemroot = '/'):
        if hostwc is None:
            vadmdir = py.path.local(os.path.expanduser('~/.vadm'))
            hostwc = vadmdir / 'hostwc'
        self.hostwc = py.path.svnwc(hostwc) 
        self.systemroot = py.path.local(systemroot)
        self.log = logger.get('vadm', 
                     debug=None,
                     user=userconsumer, 
                     info=None,
                     warn=py.log.STDERR,
                     error=py.log.STDERR,
                     fatal=py.log.STDERR)

    def create_svn_repo(self, path, _no_vadmprop=False):
        path = py.path.local(path)
        if path.check():
            if path.listdir():
                raise ValueError("directory exists and is non-empty: %s" %(path,))
        else:
            path.ensure(dir=1)
        out = py.process.cmdexec("svnadmin create %s" %(path,))
        if not _no_vadmprop:
            value = vadm.sync.getposix("/")
            wc = py.path.svnwc(py.path.local.mkdtemp())
            try:
                wc.checkout("file://%s" % path)
                wc.propset(vadm.sync.vadmpropname, vadm.sync.getposix(self.systemroot))
                wc.commit("init")
            finally:
                wc.localpath.remove()
        return path

    def cmd(self, *args):
        if not args:
            args = ['status']
        args = list(map(str, args))

        command = args.pop(0)
        # revert to 'help' for wrong commands
        if command not in commands:
            self.log.error("unknown command: %s" % command)
            command = 'help'

        command = commands[command](self)
        command.parse_options(args)
        command.execute()


class Command:
    def __init__(self, session):
        self.session = session
        self.hostwc = session.hostwc
        self.log = session.log

    def getparser(self):
        """ return a parser object containing standard options. """
        options = []
        parser = optparse.OptionParser()
        parser.add_option("-v", "--verbose", action="count", dest="verbose",
                          help="increase verbosity")
        #parser.add_option("-q", "--quiet", action="count", dest="quiet",
        #                  help="reduce output as much as sensible")
        return parser

    def set_usage(self, parser, posarghelp=None, explanation=None):
        """ set usage information on the standard parser. 

        This usage information is displayed in case of an cmdline-arg/option
        error. 

        """
        if explanation is None:
            explanation = self.__class__.__doc__

        cmdname = self.__class__.__name__[4:]
        options = "".join([x[1] for x in parser._short_opt])
        if posarghelp is None:
            if self.__class__ == cmd_config:
                text = ""
            else:
                text = "[FILE1] [FILE2] ..."
        else:
            text = posarghelp

        if explanation:
            lines = [x.strip() for x in explanation.split('\n')]
            l = textwrap.wrap(" ".join(lines), 70, 
                              initial_indent=" "*7,
                              subsequent_indent=" "*7)
            l.insert(0, '')
            text += "\n" + "\n".join(l) # explanation.strip()
        parser.usage = "vadm %s [-%s] %s" %(cmdname, options, text)

    def parse_options(self, args):
        parser = self.getparser()
        self.set_usage(parser)
        self.doparse(parser, args)

    def fail(self, msg, exc=SystemExit):
        """ write error message and raise an exception if so defined. """
        #self.session.error(msg)
        if exc:
            raise exc(msg)

    def prepare_wc(self):
        self.log.debug("checking out WC for vadm-files if necessary")
        vadm.sync.update_hostwc(self.session)
        self.log.debug("syncing files to WC. ")
        vadm.sync.all_fs2wc(self.session)

    def _getfileargs(self):
        args = self.args
        if not args: 
            args = [str(py.path.local())]
        return args 

    def target_and_wcpath(self):
        """ yield target, wcpath tuple (honour self.args if any). """
        args = self._getfileargs() 
        for fname in args: 
            target = py.path.local(fname)
            reltarget = target.relto(self.session.systemroot)
            wcpath = self.session.hostwc.join(reltarget)
            if wcpath.check(): 
                yield target, wcpath
            else:
                self.log.warn("path not versioned:", target)

    def doparse(self, parser, args, numargs=None):
        self.session.options, self.args = parser.parse_args(args)
        if self.session.options.verbose:
            self.log.set_sub(info=userconsumer) 
        if numargs is not None and len(self.args) != numargs:
            self.log.error("exactly %d positional arguments required" %(numargs,))
            print parser.usage
            raise SystemExit, 1
        #if options.verbose >=3:
        #    from vpath import svn_wc_command 
        #    svn_wc_command.DEBUG = 1
        #
class cmd_version(Command):
    """ display version info"""
    def parse_options(self, args):
        pass

    def execute(self):
        """ this produces a list of all commands together with
            their abbreviations. 
        """
        self.log.user("version: %s" %(vadm.__version__))
        self.log.user("author: holger krekel <holger at merlinux eu>")
        self.log.user("website: http://codespeak.net/vadm",)
        
class cmd_help(Command):
    """ display usage and help. """
    def parse_options(self, args):
        pass

    def execute(self):
        """ this produces a list of all commands together with
            their abbreviations. 
        """
        self.log.user("list of valid commands")
        d = {}
        for name,value in commands.items():
            d.setdefault(value, []).append(name)
        values = d.values()
        values.sort()
        for namelist in values:
            namelist.sort(lambda x,y: cmp(len(y), len(x)))
            self.log.user("   %s" % ", ".join(namelist))

class cmd_list(Command):
    """ display status information about the state of all system files. """

    def parse_options(self, args):
        parser = self.getparser()
        self.set_usage(parser)
        self.doparse(parser, args)

    def execute(self):
        self.prepare_wc()
        for target, wcpath in self.target_and_wcpath():
            status = wcpath.status(rec=True)
            for path in status.allpath(): 
                directpath = path.localpath.sep + path.relto(self.session.hostwc)
                self.log.user(directpath) 

class cmd_status(Command):
    """ display status information about the state of all system files. """

    def parse_options(self, args):
        parser = self.getparser()
        self.set_usage(parser)
        self.doparse(parser, args)

    def execute(self):
        self.prepare_wc()

        #for wcroot in (self.session.hostwc, ):
        for target, wcpath in self.target_and_wcpath():
            wcroot = self.session.hostwc

            s = wcpath.status(updates=1, rec=1)
            properties = wcpath.proplist(rec=1)
            #print vars(s)
            for p in s.allpath():
                target_p = py.path.local(p.sep + p.relto(wcroot))
                if p in s.incomplete:
                    self.log.fatal('detected incomplete svn resource %r')
                elif p in s.kindmismatch:
                    self.log.fatal('detected dir/file mismatch of svn resource %r')
                elif p in s.deleted:
                    modified = 'deleting'
                else:
                    if not p in properties:
                        if p.check(file=1):
                            self.log.warn('%r is under version control, but has no posix info, correcting ...' % target_p)
                            vadm.sync.posix_fs2wc(self.session, target_p, p)
                            self.log.fatal('added posix info, please restart command')
                        else:
                            self.log.debug("skipping %s" % p)
                            continue
                    propdict = properties[p]
                    if not propdict.has_key('vadm:posix'):
                        continue

                    #if p.isdir():
                    #    continue # XXX handle/allow directories
                    modified = ''
                    if p in s.added:
                        modified = 'added'
                    elif p in s.modified:
                        modified = 'modified'
                    if p in s.prop_modified:
                        if not modified:
                            modified = 'permchange' 
                        else:
                            modified = 'p/' + modified

                syncstate = 'insync'
                if p in s.update_available:
                    syncstate = 'notinsync'

                if (modified or syncstate != 'insync'): 
                    outmeth = self.log.user
                else:
                    outmeth = self.log.info 
                outmeth("%-10s %-9s %s" %
                        (modified, syncstate, target_p))


class cmd_diff(Command):
    """ output diff information about the given files. With no arguments
        display the diff of all system files. 
    """
    def parse_options(self, args):
        parser = self.getparser()
        self.set_usage(parser)
        self.doparse(parser, args)

    def execute(self):
        self.prepare_wc()
        for target, wcpath in self.target_and_wcpath():
            s = wcpath.diff()
            if s.strip():
                self.log.user(s) 

class cmd_blame(Command):
    """ display blame information for the given file. 
    """
    def parse_options(self, args):
        parser = self.getparser()
        self.set_usage(parser)
        self.doparse(parser, args, numargs=1)

    def execute(self):
        self.prepare_wc()
        for target, wcpath in self.target_and_wcpath():
            if not target.check():
                raise CommandError("does not exist: %s" %(target,))
            if not target.check(file=1):
                raise CommandError("not a file: %s" %(target,))
            blameentries = wcpath.blame()
            for rev, author, line in blameentries:
                self.log.user("%6d %-10s %s" %(rev, author, line.rstrip()))

class cmd_log(Command):
    """ display history information for the given files (or all files
        if no files are given. 
    """
    def parse_options(self, args):
        parser = self.getparser()
        parser.add_option("-n", "--num", action="store", dest="num", default=10, 
                          type="int", help="number of recent log entries to show") 
        self.set_usage(parser)
        self.doparse(parser, args)

    def execute(self):
        self.prepare_wc()
        for target, wcpath in self.target_and_wcpath():
            num = self.session.options.num
            l = wcpath.log()[:num]
            self.log.user("%d most recent log entries" % num)
            l.reverse()
            for i in l:
                self.log.user("-" * 70)
                self.log.user("rev %d, author %s" % (i.rev, i.author)) 
                self.log.user(i.msg)

class cmd_create(Command):
    """ create a vadm-repository as a subversion repository. 
        Directories along the provided path are automatically created. 
    """
    def parse_options(self, args):
        parser = self.getparser()
        self.set_usage(parser, posarghelp="PATH_TO_REPOSITORY")
        self.doparse(parser, args, numargs=1)

    def execute(self):
        repodir = py.path.local(self.args[0])
        if repodir.check() and repodir.listdir():
            raise CommandError("cannot create repository at: %s" %(repodir,))
        repodir.ensure(dir=1)
        self.session.create_svn_repo(repodir)
        self.log.user("created svn repository at: %s" % repodir)

class cmd_checkout(Command):
    """ checkout a vadm-repository from a svn url. """

    def parse_options(self, args):
        parser = self.getparser()
        self.set_usage(parser, posarghelp="REPOSITORYURL")
        self.doparse(parser, args, numargs=1)

    def execute(self):
        url = self.args[0]
        scheme = url.split(':')[0]
        if scheme not in ('file', 'http', 'https', 'svn+ssh'):
            url = "file://%s" % (py.path.local(url),)
        url = py.path.svnurl(url)
         
        if not url.check():
            raise CommandError("repository does not exist: %s" %(url.url))

        if self.hostwc.check() and self.hostwc.listdir():
            self.hostwc.localpath.remove()
       
        self.hostwc.checkout(url.url)
        if vadm.sync.vadmpropname not in self.hostwc.proplist():
            self.fail("missing %r property in -> not a vadm repo: %s" %(vadm.sync.vadmpropname, url,))
        self.log.info("using repository:", url.url)
        self.log.info("internal checkout directory:", self.hostwc)

class cmd_commit(Command):
    """ commit live files to the repository. With no arguments all 
        changed files will be committed.  If arguments (=paths) 
        are given then only these paths will be commited. 
        If you specify a directory only files under that directory 
        will be committed. Relative paths are also accepted (e.g. if 
        your cwd is /etc and you say 'vadm commit passwd')
    """

    def parse_options(self, args):
        parser = self.getparser()
        parser.add_option("-m", "--message", action="store", dest="message",
                          help="commit message")
        self.set_usage(parser)
        self.doparse(parser, args)

    def execute(self):
        self.prepare_wc()
        items = list(self.target_and_wcpath())
        if len(items) == 1 and items[0][0] == self.session.systemroot:
            wc = items[0][1]
            st = wc.status(rec=True)
            if not (st.modified or st.prop_modified or st.added):
                items.pop()
        if not items:
            args = " ".join(self._getfileargs())
            self.log.warn("nothing to commit at: %s" %(args))
        else:            
            commitpaths = " ".join([repr(str(y.localpath)) 
                                       for x,y in items])
            message = self.session.options.message
            if message:
                cmd = 'svn commit -m %r %s' % (message, commitpaths)
            else:
                cmd = 'svn commit %s' % (commitpaths,)
            print "executing", cmd
            ret = os.system(cmd)
            if ret:
                status = os.WEXITSTATUS(ret)
                raise CommandError("svn execution failed: %s" % cmd)
        
class cmd_add(Command):
    """ Schedule given files or directories for versioning. 
        You need to provide one or more filenames or a list 
        of files via the -f|--fromfile option.  
        Note that only a "vadm commit" will make the 
        addition permanent. 
    """

    def parse_options(self, args):
        parser = self.getparser()
        parser.add_option("-f", "--fromfile", action="store", dest="fromfile", default=None, 
                          help="read list of files from the given file")
        parser.add_option("--strict", action="store_true", dest="strict", default=False, 
                          help="raise errors on missing or already versioned file items")
        self.set_usage(parser)
        self.doparse(parser, args)
        fromfile = self.session.options.fromfile 
        if self.args and not fromfile: 
            filelist = self.args 
        elif not self.args and fromfile: 
            filelist = py.path.local(fromfile).readlines(cr=0)
        else: 
            print parser.usage
            raise CommandError("expecting either target file/directory arguments "
                               "or a file list specified with --fromfile")
        self.filelist = map(py.path.local, filelist)

    def execute(self):
        self.prepare_wc()
        strict = self.session.options.strict 
        assert not strict
        for target in self.filelist: 
            systemroot = self.session.systemroot
            if not target.relto(systemroot):
                raise CommandError(
                    "%s not relative to systemroot: %s" %(target, systemroot))
            if not target.check(): 
                warnmsg = "target path does not exist: %s" %(target,)
                if strict: 
                    raise CommandError(warnmsg) 
                else: 
                    self.log.warn(warnmsg) 
                    continue
            
            wcpath = self.hostwc.join(str(target.relto(systemroot)))
            if wcpath.check(versioned=0):
                if target.realpath() != target:
                    raise CommandError, (
                        "adding paths with link components not yet supported %r" % target)
                else:
                    wcpath.ensure(dir=target.check(dir=1))
                    if target.check(file=1): 
                        vadm.sync.content_fs2wc(self.session, target, wcpath)
                    vadm.sync.posix_fs2wc(self.session, target, wcpath)
                    wcpath.add()
                    self.log.user('added %s' % target)
            elif wcpath.check(versioned=True): 
                msg = "%s is already under version control" % target
                if strict: 
                    raise CommandError(msg) 
                else: 
                    self.log.warn(msg)
                    
class cmd_config(Command):
    """ display vadm configuration information. 
    """
    def execute(self):
        hostwc = self.session.hostwc 
        if not hostwc.check():
            self.log.error("cannot find working copy at %s" %(
                hostwc.localpath,))
            raise SystemExit, 1
        if hostwc.check(versioned=0):
            self.log.error("is not a working copy: %s" %(
                hostwc.localpath,))
            raise SystemExit, 1
            
        self.log.user("workingcopy: %s" %(self.hostwc.localpath,))
        self.log.user("repository:  %s" %(self.hostwc.svnurl(),))

class cmd_remove(Command):
    """ remove the given files from version control. 
        This will not delete the file from the filesystem. 
    """
    def parse_options(self, args):
        parser = self.getparser()
        self.set_usage(parser)
        self.doparse(parser, args)

    def execute(self):
        self.prepare_wc()

        if self.args:
            for fname in self.args:
                target = py.path.local(fname)
                reltarget = target.relto(self.session.systemroot)
                wcpath = self.hostwc.join(reltarget)
                wcpath.remove(force=1)
                self.log.user('scheduling deletion of %r from repository' % target)

class cmd_revert(Command):
    """ revert the given files to the last committed state. 
    """
    def parse_options(self, args):
        parser = self.getparser()
        self.set_usage(parser)
        self.doparse(parser, args)

    def execute(self):

        if not self.args:
            self.fail('can only revert specific files or directories.')

        self.prepare_wc()
        for target, wcpath in self.target_and_wcpath():
            out = wcpath.revert()
            if wcpath.status().unknown:
                wcpath.localpath.remove()
                self.log.user("reverted addition of %s" % target)
            else:
                if out.strip():
                    vadm.sync.wc2fs(wcpath, target)
                    self.log.user("reverted %s (from %s)" % (target, wcpath.localpath))

class CommandError(Exception):
    pass            

#________________________________________________
#
# some command aliases 
#________________________________________________

cmd_st = cmd_status
cmd_ci = cmd_commit
cmd_co = cmd_checkout
cmd_rm = cmd_remove
cmd_ls = cmd_list 

#________________________________________________
#
# dynamically collect valid commands 
#________________________________________________
commands = {}
for name, value in globals().items():
    if name.startswith('cmd_'): 
        name = name[4:]
        assert isclass(value) and issubclass(value, Command) and value != Command
        commands[name] = value

def main(*args):
    """ main entry point to execute a vadm command. 
    The 'args' encode the command, options and arguments
    in unix-cmdline style. Any output is sent through
    certain methods of the sessioniguration class so that
    you can redirect output easily. 
    """
    if not args:
        args = sys.argv[1:]
    assert os.geteuid() != 0 , "you cannot run vadm as root"
    session = Session()
    try:
        return session.cmd(*args) 
    except CommandError, e: 
        session.log.error(str(e))
        raise SystemExit, 1
    except py.error.ENOENT, e: 
        session.log.error("File Not Found: %s" % str(e))
        raise SystemExit, 2
        
