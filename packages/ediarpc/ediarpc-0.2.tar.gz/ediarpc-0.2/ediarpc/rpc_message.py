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

import message

def encode(secret, method, *args, **kwargs):
    """
    Encode a message.

    >>> secret = 'moocows'
    >>> encode(secret, 'moo', meow='cats')
    '{"params": {"meow": "cats"}, "method": "moo", "signature": "545ce308d8f3b81fc18638955571aa43f81b71007dc477d78868f7c01b754123556bd958c144db8ef3412a39cd98882207864ce83ba500c3279c40e22852da0d"}'
    """
    envelope = {'method': method, 'params': kwargs}
    return message.dumps(envelope, secret)

def decode(secret, signed_message, allow_unsigned=False):
    """
    Return a tuple of the method and kwargs.

    >>> secret = 'moocows'
    >>> message = '{"params": {"meow": "cats"}, "method": "moo", "signature": "545ce308d8f3b81fc18638955571aa43f81b71007dc477d78868f7c01b754123556bd958c144db8ef3412a39cd98882207864ce83ba500c3279c40e22852da0d"}'
    >>> decode(secret, message)
    (u'moo', {u'meow': u'cats'})
    """
    unpack_message = message.loads(signed_message, secret, allow_unsigned)
    method = unpack_message.pop('method', None)
    params = unpack_message.pop('params', None)
    return (method, params)

if __name__ == '__main__':
    import doctest
    doctest.testmod()
