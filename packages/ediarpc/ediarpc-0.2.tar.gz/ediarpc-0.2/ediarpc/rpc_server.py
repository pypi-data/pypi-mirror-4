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

import SocketServer
import rpc_message
from message import InvalidSignatureException

class RPCRequestHandler(SocketServer.StreamRequestHandler):
    allow_reuse_address = True
    def handle(self):
        while True:
            line = self.rfile.readline()
            if not line:
                break
            response = self.server.dispatch(line)
            self.wfile.write(response)

class RPCServer(SocketServer.TCPServer, RPCRequestHandler):
    def __init__(self, tuple, secret):
        SocketServer.TCPServer.__init__(self, tuple, RPCRequestHandler)
        self.funcs = {}
        self.secret = secret

    def _reply(self, method, **kwargs):
        return rpc_message.encode(self.secret, method, **kwargs)

    def _error_message(self, code, message):
        return self._reply('error_response', error_code=code, error_message=message)

    def _default_method(self, *args, **kwargs):
        return self._error_message(404, "Method not implemented")

    def dispatch(self, envelope):
        try:
            unpack_message = rpc_message.decode(self.secret, envelope)
        except InvalidSignatureException:
            return self._error_message(403, "Unauthorized, invalid passphrase")

        unpack_kwargs = unpack_message[1]

        if unpack_message[0] is None:
            return self._error_message(502, "Malformed request - missing method field")

        method = unpack_message[0]
        if self.funcs.has_key(method):
            reply_args = self.funcs[method](**unpack_kwargs)
            return self._reply(None, **reply_args)

        return self._default_method()

    def bind(self, function, name=None):
        if name is None:
            name = function.__name__
        self.funcs[name] = function

if __name__ == '__main__':
    def ping(**kwargs):
        return dict(hello=kwargs)

    server = RPCServer(('127.0.0.1', 5959), 'moocows')
    server.bind(ping)
    server.serve_forever()
