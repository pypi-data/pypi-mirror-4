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
    def __init__(self, host, port, secret, allow_untrusted=False, iterations=1000):
        self._host = host
        self._port = port
        self._secret = secret
        self._allow_untrusted = allow_untrusted
        self._iterations = iterations
        self._socket = None

    def _read_loop(self, sock):
        data = []
        end = '}\r\n'
        while True:
            try:
                packet = sock.recv(1024)
                if end in packet:
                    data.append(packet[:packet.find(end)])
                    break
                data.append(packet)
                if len(data) > 1:
                    last_pair = data[-2] + data[-1]
                    if end in last_pair:
                        data[-2] = last_pair[:last_pair.find(end)]
                        data.pop()
                        break
            except:
                break
        return ''.join(data).strip() + '}'

    def _connect(self):
        if self._socket is None:
            self._socket = socket.create_connection((self._host, self._port))

        return self._socket

    def _close(self):
        if self._socket is None:
            self._socket.close()

        self._socket = None

    def __del__(self):
        self._close()

    def _call(self, name, **kwargs):
        sock = self._connect()

        envelope = rpc_message.encode(self._secret, name, iterations=self._iterations, **kwargs) + '\r\n'
        sock.sendall(envelope) 
        response = self._read_loop(sock)

        return rpc_message.decode(self._secret, response, self._allow_untrusted, iterations=self._iterations)[1]

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
