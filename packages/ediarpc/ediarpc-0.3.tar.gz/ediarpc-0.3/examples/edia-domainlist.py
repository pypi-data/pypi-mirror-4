#!/usr/bin/env python
#
# A proof of concept script which calls the 'domain_list' method published on
# an RPC server.  This method in theory returns a dictionary of the format:
#
# {'domain-name': {'key': 'value', 'key2': 'value2'}}
#
# So we extract the key in the top-level dictionary and print it.
#

from ediarpc import rpc_client

if len(sys.argv) < 3:
    print "usage: %s hostname secret" % sys.argv[0]
    exit()

hostname = sys.argv[1]
secret = sys.argv[2].encode('ascii')

cli = rpc_client.ServerProxy(hostname, 5959, secret, True, iterations=15)

list = cli.domain_list()

for domain, stats in list.items():
    print domain
