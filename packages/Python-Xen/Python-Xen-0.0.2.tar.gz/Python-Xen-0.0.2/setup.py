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

setup(name='Python-Xen',
      version='0.0.2',
      description='Python Xen bindings using bits of libxc and libxs',
      long_description="""
A library which uses bits of the libxc and libxs Python bindings to provide basic administration
and introspection of Xen domains.

Tasks covered by this library presently include:

- Getting a list of ``Domain`` objects.
- Getting status on ``Domain`` objects.
- Shutting down, Destroying and Restarting ``Domain`` objects.
- Pausing and unpausing ``Domain`` objects.
- Getting statistics (like ``xentop``) for ``Domain`` objects.

Creation may be covered later, but it seems unnecessary.
      """,
      author='William Pitcock',
      author_email='nenolod@tortois.es',
      maintainer='William Pitcock',
      maintainer_email='nenolod@tortois.es',
      url='http://www.bitbucket.org/tortoiselabs/python-xen',
      packages=['pyxen'],
      classifiers=['License :: OSI Approved :: ISC License (ISCL)', 'Operating System :: POSIX',
                   'Topic :: System :: Systems Administration'],
      platforms=['Xen'],
     )
