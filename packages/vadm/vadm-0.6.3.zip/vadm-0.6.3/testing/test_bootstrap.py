# Copyright 2008 Holger Krekel

import py 
from vadm.cmdline import Session, CommandError

class _TestLog(dict):
    def __init__(self, session):
        super(_TestLog, self).__init__() 
        def consumer(msg):
            assert msg.keywords[0] == 'vadm'
            self.setdefault(msg.keywords[1], []).append(msg.strcontent())
        session.log.set_override(consumer) 

    def poplog(self, name="user"):
        l = self.get(name, [])
        s = "\n".join(l)
        l[:] = []
        return s

class VadmTestBase(object): 
    def setup_class(cls):
        cls.clstmpdir = py.test.ensuretemp(cls.__name__) 

    def setup_method(self, method):
        self.tmp = self.clstmpdir.join(method.__name__)
        self.wc = py.path.svnwc(self.tmp.join("wc"))
        self.repodir = self.tmp.join("sysrepo")
        self.repourl = py.path.svnurl("file://%s" %(self.repodir,))
        self.systemroot = self.tmp.ensure("systemroot", dir=1) 
        self.session = Session(self.wc, systemroot=self.systemroot)
        self.testlog = _TestLog(self.session)

class TestBootStrap(VadmTestBase):
    def test_create_fail_on_non_empty(self):
        self.repodir.ensure("somefile")
        py.test.raises(CommandError, 
            "self.session.cmd('create', self.repodir)")

    def test_create_simple_explicit(self):
        self.session.cmd('create', self.repodir)
        assert self.repodir.join("hooks").check()
        assert self.repodir.join("db").check()
        l = self.repourl.listdir()
        assert not l 
        assert self.repourl.propget("vadm:posix")

    def test_co_fail_on_missing_repo(self):
        py.test.raises(CommandError, 
            "self.session.cmd('co', self.repodir)")

    def test_co_fail_on_non_vadm_repo(self):
        self.session.create_svn_repo(str(self.repodir), _no_vadmprop=True)
        py.test.raises(SystemExit, 
            "self.session.cmd('co', self.repodir)")

    def test_co_use_existing_vadmrepo(self):
        self.session.create_svn_repo(self.repodir)
        self.repourl.mkdir("testdir")
        self.session.cmd('co', self.repodir)
        assert self.wc.join("testdir").check()
        assert self.wc.svnurl() == self.repourl

    def test_config(self):
        py.test.raises(SystemExit, "self.session.cmd('config')")
        txt = self.testlog.poplog("error")
        assert txt.find("cannot find") != -1
        self.wc.localpath.ensure(dir=1)
        py.test.raises(SystemExit, "self.session.cmd('config')")
        txt = self.testlog.poplog("error")
        assert txt.find("is not a working") != -1
        
        self.session.create_svn_repo(self.repodir)
        self.session.cmd('checkout', self.repodir)
        self.session.cmd('config')
        txt = self.testlog.poplog()
        print txt
        assert txt.find("workingcopy: %s" %(self.wc.localpath)) != -1
        assert txt.find("repository:  file://%s" %(self.repodir)) != -1
