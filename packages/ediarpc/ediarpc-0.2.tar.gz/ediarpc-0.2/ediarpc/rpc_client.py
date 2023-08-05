#!/usr/bin/env python
"""
Copyright (c) 2012, 2013 TortoiseLabs LLC

Permission to use, copy, modify, and/or distribute this software for any
purpose with or without fee is hereby granted, provided that the above
copyright notice and this permission notice appear in all copies.

This software is provided 'as is' and without any warranty, express or
implied. In no event shall the authors be liable for any damages arising
from the use of this software.
"""

import socket
import rpc_message

class ServerProxy(object):
    def __init__(self, host, port, secret, allow_untrusted=False):
        self._host = host
        self._port = port
        self._secret = secret
        self._allow_untrusted = allow_untrusted

    def _read_loop(self, sock):
        data = []
        sock.settimeout(None)
        data.append(sock.recv(1024))
        sock.settimeout(0.1)

        while True:
            try:
                data.append(sock.recv(1024))
            except:
                break

        sock.settimeout(None)
        return ''.join(data)

    def _call(self, name, **kwargs):
        sock = socket.create_connection((self._host, self._port))

        envelope = rpc_message.encode(self._secret, name, **kwargs) + '\r\n'
        sock.sendall(envelope) 
        response = self._read_loop(sock)
        sock.close()

        return rpc_message.decode(self._secret, response, self._allow_untrusted)[1]

    def __getattr__(self, name):
        """
        Create a function which makes a RPC call.
        """
        def f(*args, **kwargs):
            return self._call(name, **kwargs)

        return f

if __name__ == '__main__':
    proxy = ServerProxy('127.0.0.1', 5959, 'moocows')
    print proxy.ping(moo='cow')
