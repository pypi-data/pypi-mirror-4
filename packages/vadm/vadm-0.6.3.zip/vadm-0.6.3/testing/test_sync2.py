
import py
import os
import vadm

def setup_module(mod):
    py.test.skip("xxx tests disabled, because sync2 module not used yet")

class TestFileServer:
    def setup_class(cls):
        cls.gateway = py.execnet.PopenGateway()
        cls.tmpdir = py.test.ensuretemp(cls.__name__)
        print "using tmpdir", cls.tmpdir

    def teardown_class(cls):
        cls.gateway.exit()

    def setup_method(self, method):
        self.sync = vadm.sync2.FileServer(self.gateway)

    def teardown_method(self, method):
        self.sync.shutdown() 

    def test_getcontent(self):
        sync = self.sync
        p1 = self.tmpdir.join("hello") 
        p1.write("world")
        content = sync.getcontent(p1)
        s = p1.read()
        assert s == content 

    def test_getposix(self):
        sync = self.sync
        p1 = self.tmpdir.ensure("one", "two") 
        posixinfo = sync.getposix(p1)
        parts = p1.parts()
        for path1, (path2, (owner, group, mode)) in zip(parts, posixinfo): 
            assert path1 == path2 
            assert path1.owner() == owner 
            assert path1.group() == group 
            assert path1.mode() == mode 
            
    def test_setcontent(self):
        sync = self.sync 
        p1 = self.tmpdir.join("somefile") 
        string = "something"
        sync.setcontent(p1, string) 
        s = p1.read()
        assert s == string 

    def test_setposix(self):
        sync = self.sync
        p1 = self.tmpdir.ensure("1", "2") 
        sync.setposix(p1, mode=0500)
        sync.setposix(p1.dirpath(), mode=0550)
        assert 0777 & p1.mode() == 0500 
        assert 0777 & p1.dirpath().mode() == 0550
        sync.setposix(p1, mode=0700)
        assert p1.mode() & 0777 == 0700 

class TestSudoFileServer(TestFileServer):
    def setup_class(cls):
        cls.gateway = py.execnet.PopenGateway('sudo python -u -c "exec input()"')
        cls.tmpdir = py.test.ensuretemp(cls.__name__)
        print "using tmpdir", cls.tmpdir
