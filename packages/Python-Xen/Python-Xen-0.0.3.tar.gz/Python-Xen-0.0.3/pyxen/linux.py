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
import os.path
from .stub import BaseCollector

class LinuxStatsCollector(BaseCollector):
    def retrieve_network_statistics(self):
        lines = open("/proc/net/dev", "r").readlines()

        columnLine = lines[1]
        _, receiveCols , transmitCols = columnLine.split("|")
        receiveCols = map(lambda a:"recv_"+a, receiveCols.split())
        transmitCols = map(lambda a:"trans_"+a, transmitCols.split())

        cols = receiveCols + transmitCols

        faces = {}
        for line in lines[2:]:
            if line.find(":") < 0:
                continue

            face, data = line.split(":")
            faceData = dict(zip(cols, data.split()))
            faces[face.lstrip()] = faceData

        return faces

    def retrieve_vbd_statistics_for_domain(self, domain):
        vbds = []

        path = '/sys/devices/'
        if os.path.exists('/sys/devices/xen-backend'):
            path = '/sys/devices/xen-backend/'

        backendstore = os.listdir(path)
        for d in backendstore:
            if d[0:4] != 'vbd-':
                continue

            _, domid, dev = d.split('-')
            if int(domid) != domain:
                continue

            vbd = {}
            keystore = os.listdir(path + d + '/statistics/')
            for k in keystore:
                vbd[k] = int(open(path + d + '/statistics/' + k).readline())

            vbds.append(vbd)

        return vbds
