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

import os

from .domain import Domain
from xen.lowlevel.xs import xs
from xen.lowlevel.xc import xc

class Session(object):
    '''Wrapper object to create lower-level constructs, such as Domains.'''
    def __init__(self):
        self.xs = xs()
        self.xc = xc()
        self.collector = None

    def Domain(self, domid):
        return Domain(domid, xs=self.xs, xc=self.xc, session=self)

    def domain_list(self):
        return [self.Domain(dom['domid']) for dom in self.xc.domain_getinfo()]

    def StatsCollector(self):
        if self.collector is not None:
            return self.collector

        os_type = os.uname()[0]
        if os_type == 'Linux':
            from .linux import LinuxStatsCollector
            self.collector = LinuxStatsCollector(session=self)
        else:
            from .stub import StatsCollector
            self.collector = StatsCollector(session=self)

        return self.collector

    def Hypervisor(self):
        return Hypervisor(self)

class Hypervisor(object):
    '''Convenience class around libxc primitives.'''
    def __init__(self, session):
        self.session = session

    def dmesg(self, clear=False):
        return self.session.xc.readconsolering(clear)

    def physinfo(self):
        return self.session.xc.physinfo()

    def xeninfo(self):
        return self.session.xc.xeninfo()

    def info(self):
        return dict(list(self.physinfo().items()) + list(self.xeninfo().items()))
