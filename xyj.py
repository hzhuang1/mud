#!/usr/bin/python3

import getpass
import string
import re
import telnetlib
import time
import pdb

class Mud(telnetlib.Telnet):
    def __init__(self,host=None,port=0):
        self.window = b""
        telnetlib.Telnet.__init__(self)
        if host is not None:
            telnetlib.Telnet.open(self,host,port)

    def read_line(self):
        """Read a line until EOF; block until connection closed."""
        while not self.eof:
            buf = telnetlib.Telnet.read_some(self)  # return immediately
            self.window = self.window + buf
            if self.window == b"":
                continue
            ret = self.window.find(b"\r\n")         # find end of line
            if ret == -1:
                continue
            buf = self.window[0:ret+2]
            self.window = self.window[ret+2:]
            buf = re.sub(b"\x1b\[(\d|;)+m",b'',buf)  # remove color
            sbuf = buf.decode('gbk','ignore')
            print(sbuf)

    def read_xline(self):
        """Real a line until EOF; block until connection closed."""
        while not self.eof:
            buf = telnetlib.Telnet.read_some(self)  # return immediately
            if buf != b'':
                sbuf = buf.decode('gbk','ignore')   # ignore decoding error
            self.window = self.window + sbuf        # compose a new window
            if self.window == "":
                continue
            ret = self.window.find("\r\n")          # find end of line
            if ret == -1:
                continue
            sbuf = self.window[0:ret+2]
            self.window = self.window[ret+2:]
            sbuf = re.sub("\x1b\[(\d|;)+m",'',sbuf)  # remove color
            print(sbuf)
            return sbuf

    def expect(self,list,timeout=None):
        """Read until one from a list of a regular expressions matches."""
        re = None
        list = list[:]
        indices = range(len(list))
        for i in indices:
            if not hasattr(list[i], "search"):
                if not re: import re
                list[i] = re.compile(list[i])
        if timeout is not None:
            from time import time
            time_start = time()
        while 1:
            buf = self.read_line()
            for i in indices:
                m = list[i].search(buf)
                if m:
                    text = buf
                    return (i, m, text)
            if self.eof:
                break
            if timeout is not None:
                elapsed = time() - time_start
                if elapsed >= timeout:
                    break
                s_args = ([self.fileno()], [], [], timeout-elapsed)
                r, w, x = select.select(*s_args)
                if not r:
                    break
            if not text and self.eof:
                raise EOFError
            return (-1, None, text)

    def connect(self):
        m_words = ["[提示：如果按ENTER键后系统没有响应，请试 Ctrl-ENTER]",
                    "Welcome to Xi You Ji! Select GB or BIG5 (gb/big5):"]
        if self.sock is None:
            self.open(self,self.host,self.port)
        #while 1:
        #    self.expect(m_words)
        while True:
            buf = self.read_line()
            for i in range(len(m_words)):
                ret = buf.find(m_words[i])
                if ret != -1:
                    if i == 0:
                        self.write(b"\n")
                        continue
                    elif i == 1:
                        self.write(b"gb\n")
                        continue
            print(buf)
            continue
        """
        if self.sock is None:
            self.open(self,self.host,self.port)
        while True:
            buf = self.read_line()
            ret = buf.find("[提示：如果按ENTER键后系统没有响应，请试 Ctrl-ENTER]")
            if ret == -1:
                continue
            self.write(b"\n")
            break
        while True:
            buf = self.read_line()
            ret = buf.find("Welcome to Xi You Ji! Select GB or BIG5 (gb/big5):")
            self.write(b"gb\n")
            print(buf)
        """

if __name__ == "__main__":
    #server = "202.91.243.150"
    #port = "6666"
    #user = "roald"
    #passwd = "99bit78"
    server = "192.168.11.102"
    port = "7777"
    user = "zixin"
    passwd = "asdfg"

    mud = Mud(server,port)
    mud.connect()
    while True:
        buf = mud.read_line()
        print(".")
        if buf == "":
            time.sleep(1)
        else:
            print(buf)
	#tn = telnet_login(server,port,user,passwd)
