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

from collections import defaultdict

def _add_dictionary(a, b):
    newdict = defaultdict(int, a)
    for k,v in b.iteritems():
        newdict[k] += v
    return newdict

class BaseCollector(object):
    def __init__(self, session):
        self.session = session

    def retrieve_network_statistics(self):
        return None

    def retrieve_network_statistics_for_device(self, device):
        tuple = self.retrieve_network_statistics()
        if tuple is not None and tuple.has_key(device):
            return tuple[device]
        return None

    def _network_device_for_domain(self, domid, netid=0):
        return "vif%d.%d" % (domid, netid)

    def retrieve_network_statistics_for_domain(self, domid):
        dev = self._network_device_for_domain(domid)
        return self.retrieve_network_statistics_for_device(dev)

    def retrieve_vbd_statistics_for_domain(self, domain):
        return None

    def retrieve_vbd_synopsis_for_domain(self, domain):
        stats = self.retrieve_vbd_statistics_for_domain(domain)
        combined = {}

        for vol in stats:
            combined = _add_dictionary(combined, vol)

        return combined

class StatsCollector(BaseCollector):
    pass
