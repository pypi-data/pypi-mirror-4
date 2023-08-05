#!/usr/bin/env python

__version__ = '1.0'

from random import randint
import socket
import struct

class Noeq:

    def __init__(self, token, *servers):
        if len(servers) == 0:
            raise ValueError("List of servers cannot be blank")
        if token != None and len(token) > 255:
            raise ValueError("token is too long")
        self.token   = (token or "")
        self.conn    = None
        # Validate and parse server info
        self.servers = []
        for server in servers:
            (host,port) = server.split(':')
            self.servers.append((host,port,))

    def connect(self):
        # pick a random server from the list
        num = randint(0,len(self.servers)-1)
        server = self.servers[num]
        #print "Connect to server {}".format(server)
        self.conn = socket.create_connection(server)
        self.auth()

    def disconnect(self):
        self.conn.shutdown(socket.SHUT_RDWR)
        self.conn.close()

    def auth(self):
        if self.token != "":
            self.conn.sendall("\000{:c}{:s}".format(len(self.token), self.token))

    def get(self, num=1):
        if num < 1:
            num = 1
        if num > 255:
            raise ValueError("requested more than 255 ids")
        # TODO: Thread lock
        self.conn.send(struct.pack('B', num))
        # Read the results
        data = self.conn.recv(num * 8)
        ids = struct.unpack('!{}Q'.format(num), data)
        return ids

    def getOne(self):
        return get(1)[0]

if __name__ == '__main__':
    c = Noeq("",'localhost:4444')
    c.connect()
    print c.get(40)
    c.disconnect()

