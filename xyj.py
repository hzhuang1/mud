#!/usr/bin/python3

import getpass
import select
import socket
import string
import sys
import re
import telnetlib
import time
import pdb

class Mud():
    def __init__(self,user,passwd,client):
        self.user = user
        self.passwd = passwd
        self.login = 0
        self.client = client

    def connect(self,sbuf):
        """login mud"""
                   #"您上次连线的时间是：",
                   #"重新连线完毕。",
        m_words = ["Select GB or BIG5 (gb/big5):",
                   "您是否是中小学学生或年龄更小？(yes/no)",
                   "您的英文名字：（新玩家请键入 new 注册）",
                   "请输入相应密码：",
                   ">"]
        for i in range(len(m_words)):
            ret = sbuf.find(m_words[i])
            if ret != -1:
                if i == 0:
                    self.client.sock.sendall(b"gb\n")
                elif i == 1:
                    self.client.sock.sendall(b"no\n")
                elif i == 2:
                    user = self.user.encode('gbk','ignore') + b"\n"
                    self.client.sock.sendall(user)
                elif i == 3:
                    passwd = self.passwd.encode('gbk','ignore') + b"\n"
                    self.client.sock.sendall(passwd)
                elif i == 4:
                    self.login = 1
                    self.client.sock.sendall(b"set brief 1\n")
                    self.client.sock.sendall(b"set brief_message 1\n")
                    self.client.sock.sendall(b"set no_teach 1\n")
                    self.client.sock.sendall(b"set no_follow 1\n")
                    self.client.sock.sendall(b"set wimpy 40\n")
                break
        return self.login

    def disconnect(self):
        if self.login == 1:
            self.client.sock.sendall("quit\n")

    def parse(self,line):
        sbuf = line.decode('gbk','ignore')
        #sys.stdout.write(sbuf)
        #sys.stdout.flush()

        if self.login == 0:
            if self.connect(sbuf) == 0:
                return
        sys.stdout.write(sbuf)
        sys.stdout.flush()

class Telnet():
    def __init__(self, user, passwd, server=None, port=0,
                 timeout=socket._GLOBAL_DEFAULT_TIMEOUT):
        self.eof = 0
        self.line = b''
        self.rawq = b''
        self.server = server
        self.port = port
        self.sock = None
        self.timeout = timeout
        self.user = user
        self.passwd = passwd
        self.mud = None
        if server is not None:
            self.open(server, port, timeout)

    def __del__(self):
        if self.mud:
            self.mud.disconnect()
        self.close()

    def open(self, server, port, timeout=socket._GLOBAL_DEFAULT_TIMEOUT):
        self.eof = 0
        self.server = server
        self.port = port
        self.timeout = timeout
        self.sock = socket.create_connection((server, port), timeout)
        self.sock.setblocking(0)

    def close(self):
        """Close the connection."""
        if self.sock:
            self.sock.close()
        self.sock = 0
        self.eof = 1

    def fileno(self):
        """Return the fileno() of the socket object used internally."""
        return self.sock.fileno()

    def readline(self):
        self.line = b''
        while not self.eof and self.sock_avail():
            buf = self.sock.recv(1024)
            self.eof = (not buf)
            self.rawq = self.rawq + buf
            self.rawq = re.sub(b"\x1b\[(\d|;)+m",b'',self.rawq) # remove color
        if self.rawq is not None:
            ret = self.rawq.find(b"\r\n")                       # find end of line
            if ret == -1:
                self.line = self.rawq
                self.rawq = b''
            else:
                self.line = self.rawq[0:ret+2]
                self.rawq = self.rawq[ret+2:]
#            print(self.line)
        return self.line

    def sock_avail(self):
        """Test whether data is available on the socket."""
        return select.select([self], [], [], 0) == ([self], [], [])

    def interact(self):
        """Interaction function, emulates a very dumb telnet client."""
        if sys.platform == "win32":
            print("can't run in win32 platform\n")
            return
        self.mud = Mud(self.user, self.passwd, self)
        while 1:
            rfd, wfd, xfd = select.select([self, sys.stdin], [], [])
            if self in rfd:
                try:
                    while 1:
                        data = self.readline()
                        if data != b'':
                            self.mud.parse(data)
                        else:
                            break   # finish to read line
                except EOFError:
                    print('*** Connection closed by remote host ***')
                    break
            if sys.stdin in rfd:
#                print("hx")
                cmd = sys.stdin.readline().encode('gbk','ignore')
                if not cmd:
                    break
                self.sock.sendall(cmd)

if __name__ == "__main__":
    hd = Telnet("zixin", "asdfg", "192.168.11.102", "7777")
    #hd = Telnet("alphadf", "123456", "202.91.243.150", "7777")
    while 1:
        hd.interact()

