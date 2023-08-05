#!/usr/bin/env python
#
# A proof of concept console client running over the TortoiseLabs Cloud RPC layer.
# We publish a Xen event-channel onto the RPC layer, and then can manipulate it by
# reading and writing the event-channel.  This is wrapped for security reasons, to
# restrict to just the console event-channel on the RPC server, but the same code
# could be used for any event-channel, such as network or block i/o, allowing for
# example, a network device that tunnels back to the customer over RPC messaging,
# or a block i/o device that works the same way, or perhaps a file system exposed
# via event-channel somehow.
#

import sys
import select
import termios
import tty
import re

from ediarpc import rpc_client

if len(sys.argv) < 4:
    print "usage: %s hostname secret domain" % sys.argv[0]
    exit()

hostname = sys.argv[1]
secret = sys.argv[2].encode('ascii')
domname = sys.argv[3]

print "Attempting to attach to console of VPS %s on host %s with secret %s" % (domname, hostname, secret)

cli = rpc_client.ServerProxy(hostname, 5959, secret, True, iterations=15)

strip_vt1_rx = re.compile('\x1b(\[|\(|\))[;?0-9]*[0-9A-Za-z]')
strip_vt2_rx = re.compile('[\x03|\x1a]')

def can_read_pty(pty):
    return select.select([pty], [], [], 0) == ([pty], [], [])

def write_to_console(cli, pty):
    data = []

    while True:
        if can_read_pty(pty) is False:
            break
        data.append(pty.read(1))

    if len(data) > 0:
        bytes = ''.join(data)
        bytes = strip_vt1_rx.sub('', bytes)
        bytes = strip_vt1_rx.sub('', bytes)
        bytes = strip_vt2_rx.sub('', bytes)
        cli.console_write(domname=domname, bytes=bytes)

old_settings = termios.tcgetattr(sys.stdin)
try:
    tty.setraw(sys.stdin.fileno())

    while True:
        data = cli.console_read(domname=domname, bytes=4096)
        csd = data['console_data']
        csd = strip_vt1_rx.sub('', csd)
        csd = strip_vt1_rx.sub('', csd)
        csd = strip_vt2_rx.sub('', csd)
        sys.stdout.write(csd)
        write_to_console(cli, sys.stdin)
finally:
    termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)
