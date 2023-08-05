from test_bootstrap import VadmTestBase, CommandError 
import py
import vadm

class TestSingleCommands(VadmTestBase):
    def setup_method(self, method):
        super(TestSingleCommands, self).setup_method(method)
        print "repodir", self.repodir
        self.session.cmd("create", self.repodir)
        self.session.cmd("co", "file://%s" % (self.repodir,))

    def test_version(self):
        self.testlog.poplog("user")
        self.session.cmd('version', )
        txt = self.testlog.poplog("user")
        assert txt.find(vadm.__version__) != -1
        #assert txt.find(vadm.__pkg__.author) != -1
        #assert txt.find(vadm.__pkg__.author_email) != -1

    def test_commit_nothing(self):
        self.session.cmd('commit', '-m', 'x', self.systemroot)
        txt = self.testlog.poplog("warn")
        assert txt.find("nothing to commit") != -1

    def test_commit_fails(self):
        testpath = self.systemroot.join('etc','passwd').ensure()
        self.session.cmd('add', testpath)
        py.test.raises(CommandError, 
            "self.session.cmd('commit', '-m', 'x', testpath)")
        #txt = self.testlog.poplog("error")
        #assert txt.find("child") != -1

    def test_commit_subsubchange(self):
        testpath = self.systemroot.ensure('etc', dir=True)
        self.session.cmd('add', testpath)
        self.session.cmd('ci', "-m", "c", testpath)
        txt = self.testlog.poplog("warn")
        txt = self.testlog.poplog("user")
        testpath = testpath.ensure("passwd")
        self.session.cmd('add', testpath)
        self.session.cmd('ci', "-m", "c", self.systemroot)
        txt = self.testlog.poplog("warn")
        print txt
        assert txt.find("nothing to commit") == -1

    def test_add_outside_systemroot(self):
        py.test.raises(CommandError, 
            "self.session.cmd('add', self.systemroot.dirpath())")

    def test_add_works_relative_to_systemrootself(self):
        testpath = self.systemroot.ensure('etc','passwd')
        self.session.cmd('add', testpath)
        p = self.session.hostwc.join("etc", "passwd") 
        assert p.check()
        self.testlog.poplog('warn')
        self.session.cmd('status', self.systemroot.dirpath())
        txt = self.testlog.poplog('warn')
        assert txt.find("path not versioned")

    def test_addfile_numeric_owner(self, monkeypatch):
        testpath = self.systemroot.ensure('pseudo-numeric')
        monkeypatch.setattr(py.std.pwd, 'getpwuid', lambda x: {}[3])
        self.session.cmd('add', testpath)
        assert not self.testlog.poplog('error')
        txt = self.testlog.poplog('user')
        assert txt.find("added") != -1

    def test_addfile_numeric_group(self, monkeypatch):
        testpath = self.systemroot.ensure('pseudo-numeric')
        monkeypatch.setattr(py.std.grp, 'getgrgid', lambda x: {}[3])
        self.session.cmd('add', testpath)
        assert not self.testlog.poplog('error')
        txt = self.testlog.poplog('user')
        assert txt.find("added") != -1

    def test_addfile_revert_diff_log_blame(self):
        testpath = self.systemroot.join('etc','passwd').ensure()
        self.session.cmd('add', testpath)
        assert not self.testlog.poplog('error')
        txt = self.testlog.poplog('user')
        assert txt.find("added") != -1
        self.session.cmd('status', str(testpath.dirpath()))
        res = self.testlog.poplog("user") 
        assert res.find('add') != -1 
        self.session.cmd('commit', '-m', 'test_add_message', self.systemroot)
        assert not self.testlog.poplog('error')
        self.testlog.clear()
        testpath.write('qwesomething else')
        self.session.cmd('diff', testpath)
        txt = self.testlog.poplog('user')
        print txt
        assert txt.find("+++") != -1

        self.session.cmd('revert', str(testpath))
        self.session.cmd('diff', str(testpath))
        #print "\n ".join([" ".join(args) for args in self.conf._result])
        assert self.testlog['user'] 
        self.testlog.poplog('user')
        assert not self.testlog['user'] 
        self.session.cmd('log', self.systemroot)
        assert self.testlog['user'] 
        self.testlog.poplog('user')

        self.session.cmd("blame", testpath)
        print self.testlog['user'] 
    
    def test_removefile(self):
        print "systemroot", self.systemroot
        testpath = self.systemroot.ensure('etc','something')
        self.session.cmd('add', testpath)
        self.session.cmd('commit', '-m', 'tempadd-to-remove', self.systemroot)
        self.session.cmd('remove', testpath)
        self.session.cmd('commit', '-m', 'tempadd-removed', testpath)
        assert testpath.check()
        wctestpath = self.wc.join(testpath.relto(self.systemroot))
        assert not wctestpath.localpath.check()
