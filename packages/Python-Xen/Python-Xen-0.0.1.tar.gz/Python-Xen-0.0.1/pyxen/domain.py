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

def _lookup_raw_stats(xc, domid):
    domains = xc.domain_getinfo()
    for dom in domains:
        if dom['domid'] == domid: return dom

    return None

class Domain(object):
    def __init__(self, domid, xs, xc, session):
        self.xs = xs
        self.xc = xc
        self.session = session

        tx = self.xs.transaction_start()

        self.domid = domid
        self.xs_prefix = '/local/domain/%d' % self.domid

        self._tty = self.xs.read(tx, self.xs_prefix + '/console/tty')
        self.name = self.xs.read(tx, self.xs_prefix + '/name')
        
        self.xs.transaction_end(tx)

    def __repr__(self):
        return "<Domain: '%s' (%s) [%d]>" % (self.name, self.domid, self.state())

    def _shutdown(self, reason='poweroff'):
        tx = self.xs.transaction_start()

        prefix = self.xs_prefix + '/control/shutdown'
        self.xs.write(tx, prefix, reason)

        self.xs.transaction_end(tx)

    def shutdown(self):
        self._shutdown()

    def reboot(self):
        self._shutdown(reason='reboot')

    def destroy(self):
        self.xc.destroy_domain(self.domid)

    def _state(self, rawstat):
        for state in ['blocked', 'running', 'paused', 'dying', 'shutdown', 'crashed']:
            if rawstat[state] != 0: return state

    def _rawstat(self):
        rawstat = _lookup_raw_stats(self.xc, self.domid)

        if rawstat is None:
            return dict()

        return rawstat

    def state(self):
        return self._state(self._rawstat())

    def stats(self):
        rawstat = self._rawstat()
        collector = self.session.StatsCollector()

        data = {
           'name': self.name,
           'cputime_sec': float(rawstat['cpu_time']) / 1000000000,
           'vcpu_count': rawstat['online_vcpus'],
           'state': self._state(rawstat),
           'current_mem_kb': rawstat['mem_kb'],
           'maximum_mem_kb': rawstat['maxmem_kb'],
        }

        data['netif'] = collector.retrieve_network_statistics_for_domain(self.domid)
        data['blkif'] = collector.retrieve_vbd_synopsis_for_domain(self.domid)

        return data

    def get_console_pty(self):
        return self._tty
