'''
Created on 2013-3-22

@author: stone
'''

from pdb import Pdb
from socket import socket, AF_INET, SOCK_STREAM, SOL_SOCKET, SO_REUSEADDR , SHUT_RDWR
from threading import Lock, Thread, Condition

class RpdbIO:
    '''a proxy io for remote pdb.'''

    def __init__(self):
        self.sockio = None
        self.addr = None
        self.lock = Lock()
    
    def close(self):
        self.lock.acquire()
        try:
            if self.sockio: 
                self.sockio._sock.shutdown(SHUT_RDWR)
                self.sockio.close()
                self.sockio = None
        finally:
            self.lock.release()

    def flush(self):
        self.lock.acquire()
        try:
            if self.sockio: 
                self.sockio.flush()
        finally:
            self.lock.release()

    def write(self, data):
        self.lock.acquire()
        try:
            if self.sockio: 
                self.sockio.write(data)
        finally:
            self.lock.release()

    def writelines(self, lines):
        self.lock.acquire()
        try:
            if self.sockio: 
                self.sockio.writelines(lines)
        finally:
            self.lock.release()

    def read(self, size= -1):
        self.lock.acquire()
        try:
            return self.sockio.read(size) if self.sockio else 0
        finally:
            self.lock.release()

    def readline(self, size= -1):
        self.lock.acquire()
        try:
            return self.sockio.readline(size) if self.sockio else []
        finally:
            self.lock.release()

    def readlines(self, sizehint=0):
        self.lock.acquire()
        try:
            return self.sockio.readlines(sizehint) if self.sockio else []
        finally:
            self.lock.release()
            
    def switch(self, sockio, addr):
        self.lock.acquire()
        try:
            self.sockio = sockio
            self.addr = addr
        finally:
            self.lock.release()

class Rpdb(Pdb):
    '''Remote PDB Debugger'''

    def __init__(self, port=8787, suspend=True):
        self.con = Condition()
        # pdb server
        self.skt = socket(AF_INET, SOCK_STREAM)
        self.skt.setsockopt(SOL_SOCKET, SO_REUSEADDR, True)
        self.skt.bind(('0.0.0.0', port))
        self.skt.listen(1)
        self._listen()
        # debug io
        self.io = RpdbIO()
        self.debugging = False
        self.suspend = suspend
        # init pdb
        Pdb.__init__(self, stdin=self.io, stdout=self.io)
    
    def _listen(self):
        def accept():
            while True:
                client , client_addr = self.skt.accept()
                if self.suspend:
                    self.con.acquire()
                    try:
                        self.con.notify_all()
                    finally:
                        self.con.release()
                if self.debugging:
                    client.send('Rpdb(%s:%s) already started.\r\n' % self.io.addr) 
                    client.shutdown(SHUT_RDWR)
                    client.close()
                    continue
                client_io = client.makefile('rw') 
                self.io.switch(client_io, client_addr)
                self.debugging = True
                print 'Rpdb(%s:%s) debugger: starting.' % self.io.addr
        t = Thread(target=accept)
        t.setDaemon(True)
        t.start()

    def set_trace(self, frame=None):
        if self.suspend:
            self.con.acquire()
            try:
                while not self.debugging:
                    self.con.wait()
                self.suspend= False
            finally:
                self.con.release()
        if self.debugging:
            Pdb.set_trace(self, frame=frame)

    def do_quit(self, arg):
        print 'Rpdb(%s:%s) debugger: stoped.' % self.io.addr
        self.io.close()
        self.skt.close()
        return Pdb.do_quit(self, arg)
    do_exit = do_q = do_quit

    def do_xquit(self, arg):
        print 'Rpdb(%s:%s) debugger: stoped.' % self.io.addr
        self.debugging = False
        Pdb.clear_all_breaks(self)
        Pdb.set_continue(self)
        self.io.close()
        return True 
    do_EOF = do_xq = do_xquit

    def help_xquit(self):
        self.io.writelines(['''xq(uit) - Quit safely from the debugger.
The program being executed is continued(not abored).
'''])
        self.io.flush()
    help_xq = help_xquit
