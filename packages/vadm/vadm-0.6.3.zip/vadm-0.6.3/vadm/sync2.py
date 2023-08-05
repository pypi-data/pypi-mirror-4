# Copyright 2008, Holger Krekel. Licensed under GPL V3.
"""

NOT IN USE (sync.py is in use for now)
module for copying data from a sudo process to a local user process. 

XXX use "copy" insteaed of setcontent/getcontent 

"""
from __future__ import generators

import py 

# property for storing posix owner/group/permission information
posixprop = 'vadm:posix'

class FileServer: 
    def __init__(self, gateway): 
        self.gateway = gateway
        self._chan = self.gateway.remote_exec("""
            import py
            for item in channel: 
                command, args = item
                result = None
                path = py.path.local(args[0])
                if command == "getcontent":
                    result = path.read()
                elif command == "getposix":
                    result = [(str(p), (p.owner(), p.group(), p.mode()))
                                for p in path.parts()]
                elif command == "setcontent":
                    path.write(args[1])
                elif command == "setposix":
                    owner, group, mode = args[1]
                    if owner is not None or group is not None:
                        owner = owner or path.owner()
                        group = group or path.group()
                        path.chown(owner, group)
                    if mode is not None:
                        path.chmod(mode) 
                elif command == "shutdown":
                    channel.send(None)
                    break 
                channel.send(result) 
        """)

    def shutdown(self):
        self._chan.send(("shutdown", (None,)))
        self._chan.waitclose()

    def getcontent(self, path):
        self._chan.send(("getcontent", (str(path),)))
        return self._chan.receive()

    def getposix(self, path):
        self._chan.send(("getposix", (str(path),)))
        return self._chan.receive() 

    def setcontent(self, path, data):
        self._chan.send(("setcontent", (str(path), str(data))))
        x = self._chan.receive()
        return 

    def setposix(self, path, owner=None, group=None, mode=None):
        self._chan.send(("setposix", (str(path), (owner, group, mode))))
        x = self._chan.receive()
        return 


class PosixInfo(object):
    def __init__(self, path, owner, group, mode):
        self.path = path
        self.owner = owner
        self.group = group
        self.mode = mode

