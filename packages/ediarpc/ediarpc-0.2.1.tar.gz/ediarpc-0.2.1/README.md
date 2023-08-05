# ediarpc

This is the RPC definition for Edia and some code for it.  It is meant to be used as a git submodule,
and is shared by a few tortoiselabs products for RPC calling.

## Using this as a Client

Using this as a Client is simple enough, usually.  Here is a sample interactive python session:

```
>>> from ediarpc import rpc_client
>>> cli = rpc_client.ServerProxy('localhost', 5959, 'moocows')
>>> cli.ping()
{u'hello': {}}
>>> cli.ping(hello='world')
{u'hello': {u'hello': u'world'}}
>>> cli.ping(key='value', key2=['list', 'of', 'values'], key3=True, key4=25.3)
{u'hello': {u'key3': True, u'key2': [u'list', u'of', u'values'], u'key': u'value', u'key4': 25.3}}
```

This is from a server which has a single method `ping(...)` which simply returns back the `kwargs`
list.

## Using this as a Server

Simply `bind()` any function which takes a `kwargs` list and then run the server:

```
>>> from ediarpc import rpc_server
>>> def ping(**kwargs):
...     return dict(hello=kwargs)
...
>>> server = rpc_server.RPCServer(('127.0.0.1', 5959), 'moocows')
>>> server.bind(ping)
>>> server.serve_forever()
```

## What happens if you don't use the correct passphrase?

If you're running with signature checking, this happens:

```
>>> from ediarpc import rpc_client
>>> cli = rpc_client.ServerProxy('localhost', 5959, 'wrongpass')
>>> cli.ping(hello='world')
Traceback (most recent call last):
  ...
ediarpc.message.InvalidSignatureException
```

But why does that happen, you're probably wondering.  Lets disable signature
checking:

```
>>> from ediarpc import rpc_client
>>> cli = rpc_client.ServerProxy('127.0.0.1', 5959, 'wrongpass', allow_untrusted=True)
>>> cli.ping(hello='world')
{u'error_message': u'Unauthorized, invalid passphrase', u'error_code': 403}
```

The error message is signed by the RPC server.  But since the error is signed using
a different passphrase, we don't trust the authenticity of it.

## Call syntax

```
{
	"signature": "...",
	"method": "...",
	"params": {
		"key": "value",
		"key2": "value2"
	}
}
```

## Signature generation

The signature is PBKDF2(SHA512(unsigned_json), SECRET) with a 64 bit keylength in hexadecimal.

`unsigned_json` is basically JSON as prepared by python's `json.dumps()`, as what we're signing is
the structure collapsed to that state.

## FAQ

### No TLS?!

For our specific application, TLS is unnecessary.  We will add it eventually, though.

### No PubSub?!

See answer to the TLS question.

