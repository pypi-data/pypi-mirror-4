#!/usr/bin/env python
"""
Copyright (c) 2012, 2013 TortoiseLabs LLC

Permission to use, copy, modify, and/or distribute this software for any
purpose with or without fee is hereby granted, provided that the above
copyright notice and this permission notice appear in all copies.

This software is provided 'as is' and without any warranty, express or
implied. In no event shall the authors be liable for any damages arising
from the use of this software.

The message module can be used to yield signed JSON structures, like so:

>>> secret = '592783ded97d505759a8b25248c3fc5b'
>>> message = { 'moo': 'cow' }
>>> dumps(message, secret)
'{"moo": "cow", "signature": "b617fdca6b994fa3cb45ea744e3b66f6daee37e24cd1e6df50a6ff38094549a412498c5830144000d3ed451efd39934a6cdc495cb0c86c892f66162a944e6025"}'
"""

import json
import hashlib

from pbkdf2 import pbkdf2_hex

import copy
from collections import OrderedDict

def serializable_dict(d):
    """
    Prepare a dictionary for safe serialization to JSON.

    >>> d = {'moo': 'cow', 'cow': {'septic': 'tank', 'grass': 'greener'}}
    >>> od = serializable_dict(d)
    >>> od
    OrderedDict([('cow', OrderedDict([('grass', 'greener'), ('septic', 'tank')])), ('moo', 'cow')])
    >>> import json
    >>> json.dumps(od)
    '{"cow": {"grass": "greener", "septic": "tank"}, "moo": "cow"}'
    """
    li = []
    for item in d.items():
        if isinstance(item[1], dict):
            li.append((item[0], serializable_dict(item[1])))
        else:
            li.append((item[0], item[1]))
    return OrderedDict(sorted(li))

class Message(object):
    """
    A class object which wraps a JSON structure providing signature
    and validation services.

    An example of using the constructor:
    >>> m = Message({ 'moo': 'cow' }, '592783ded97d505759a8b25248c3fc5b')
    >>> m.payload_json()
    '{"moo": "cow"}'
    """
    def __init__(self, obj, secret, expected_hash=None, iterations=1000):
        """
        The constructor for the Message object.

        Giving it an unsigned object should yield the following kind of object:

        >>> m = Message({'moo': 'cow'}, '592783ded97d505759a8b25248c3fc5b')
        >>> m.secret == '592783ded97d505759a8b25248c3fc5b'
        True
        >>> m.obj
        {'moo': 'cow'}
        >>> m.expected_hash
        """
        self.obj = obj.copy()
        self.secret = secret
        self.expected_hash = expected_hash
        self.iterations = iterations

    def payload_json(self):
        """
        Returns the inner 'payload' JSON structure without the signature attached.

        >>> m = Message({'moo': 'cow'}, '592783ded97d505759a8b25248c3fc5b')
        >>> m.payload_json()
        '{"moo": "cow"}'
        """
        return json.dumps(serializable_dict(self.obj))

    def signature(self):
        """
        Calculates the signature for the message.

        The signature is just a PBKDF2 hash of the payload toasted against the secret, which is 64 bytes long.

        >>> m = Message({'moo': 'cow'}, '592783ded97d505759a8b25248c3fc5b')
        >>> m.signature()
        'b617fdca6b994fa3cb45ea744e3b66f6daee37e24cd1e6df50a6ff38094549a412498c5830144000d3ed451efd39934a6cdc495cb0c86c892f66162a944e6025'
        """
        signature = pbkdf2_hex(self.payload_json(), self.secret, iterations=self.iterations, keylen=64, hashfunc=hashlib.sha512)
        return signature

    def dumps(self, pretty_print=False):
        """
        Dumps the message with the signature calculated and attached.

        >>> m = Message({'moo': 'cow'}, '592783ded97d505759a8b25248c3fc5b')
        >>> m.dumps()
        '{"moo": "cow", "signature": "b617fdca6b994fa3cb45ea744e3b66f6daee37e24cd1e6df50a6ff38094549a412498c5830144000d3ed451efd39934a6cdc495cb0c86c892f66162a944e6025"}'
        """
        envelope = self.obj
        envelope['signature'] = self.signature()

        if pretty_print:
            return json.dumps(envelope, indent=4, separators=(',', ': '))

        return json.dumps(envelope)

    def validate(self):
        """
        Validates the message against the expected signature.  If the message is unsigned, this
        always returns True.

        >>> m = Message({'moo': 'cow'}, '592783ded97d505759a8b25248c3fc5b')
        >>> m.validate()
        True
        >>> m = Message({'moo': 'cow'}, '592783ded97d505759a8b25248c3fc5b', 'b617fdca6b994fa3cb45ea744e3b66f6daee37e24cd1e6df50a6ff38094549a412498c5830144000d3ed451efd39934a6cdc495cb0c86c892f66162a944e6025')
        >>> m.validate()
        True
        >>> m = Message({'moo': 'cow'}, '592783ded97d505759a8b25248c3fc5b', 'abcdef123456')
        >>> m.validate()
        False
        """
        if self.expected_hash is None:
            return True

        return (self.signature() == self.expected_hash)

    def payload(self):
        """
        Returns the message payload.

        >>> structure = {'moo': 'cow'}
        >>> m = Message(structure, '592783ded97d505759a8b25248c3fc5b')
        >>> m.payload()
        {'moo': 'cow'}
        >>> m.payload() == structure
        True
        """
        return self.obj

class InvalidSignatureException(Exception):
    pass

def loads(json_data, secret, allow_unsigned=False, iterations=1000):
    """
    Unpack a JSON envelope containing an Edia RPC message.

    >>> secret = '592783ded97d505759a8b25248c3fc5b'
    >>> message = '{"moo": "cow", "signature": "b617fdca6b994fa3cb45ea744e3b66f6daee37e24cd1e6df50a6ff38094549a412498c5830144000d3ed451efd39934a6cdc495cb0c86c892f66162a944e6025"}'
    >>> loads(message, secret)
    {u'moo': u'cow'}
    >>> message = '{"moo": "cow", "signature": "abcdef123456"}'
    >>> loads(message, secret)
    Traceback (most recent call last):
        ...
    InvalidSignatureException
    >>> message = '{"moo": "cow"}'
    >>> loads(message, secret)
    Traceback (most recent call last):
        ...
    InvalidSignatureException
    >>> loads(message, secret, allow_unsigned=True)
    {u'moo': u'cow'}
    """
    envelope = json.loads(json_data)

    signature = envelope.pop('signature', None)
    if signature is None and allow_unsigned is not True:
        raise InvalidSignatureException()

    message = Message(envelope, secret, signature, iterations)
    if message.validate() is not True and allow_unsigned is not True:
        raise InvalidSignatureException()

    return message.payload()

def dumps(obj, secret, pretty_print=False, iterations=1000):
    """
    Pack a dictionary into an Edia RPC message.

    >>> secret = '592783ded97d505759a8b25248c3fc5b'
    >>> message = {'moo': 'cow'}
    >>> signed_message = dumps(message, secret)
    >>> signed_message
    '{"moo": "cow", "signature": "b617fdca6b994fa3cb45ea744e3b66f6daee37e24cd1e6df50a6ff38094549a412498c5830144000d3ed451efd39934a6cdc495cb0c86c892f66162a944e6025"}'
    >>> signed_message == dumps(message, secret)
    True
    >>> unpack_message = loads(signed_message, secret)
    >>> unpack_message == message
    True
    >>> signed_message == dumps(unpack_message, secret)
    True
    """
    return Message(obj, secret, iterations=iterations).dumps(pretty_print)

if __name__ == '__main__':
    import doctest
    doctest.testmod()
