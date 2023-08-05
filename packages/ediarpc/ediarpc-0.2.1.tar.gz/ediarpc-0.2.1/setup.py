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

from distutils.core import setup

setup(name='ediarpc',
      version='0.2.1',
      description='A JSON-based RPC calling framework which supports inline signatures derived from passphrases',
      long_description="""
A library which provides JSON-based RPC calls over TCP sockets with inline signatures to
prove authenticity between two trusted parties.

Provides a ``ServerProxy`` like object for abstracting the details of the RPC system behind
python.""",
      author='William Pitcock',
      author_email='nenolod@tortois.es',
      url='http://bitbucket.org/tortoiselabs/ediarpc',
      packages=['ediarpc'],
      classifiers=['License :: OSI Approved :: ISC License (ISCL)', 'Operating System :: POSIX',
                   'Topic :: System :: Systems Administration'])

