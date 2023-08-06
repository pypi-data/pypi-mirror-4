# Python-Xen

Copyright (c) 2012, 2013 TortoiseLabs LLC.

This software is free but copyrighted.  See COPYING.md for exact terms and conditions.

## What?

This is a lightweight Python binding for Xen which allows some manipulation of virtual machines.  Specifically,
it supports the following:

* Listing all running domains (which then can be iterated over)
* Stopping (both forcefully and safely) domains
* Getting a PTY handle for a domain (so that one may read or write from the PTY)
* Collecting state information, including:

    - Performance counters (both hypervisor and xen-backend driver counters)
    - Run-queue state (blocked, dying, stopped, paused, etcetera)
    - Amount of memory consumed by the domain
    - Name of the domain
    - Maximum memory limit for the domain (memory hotplug)
    - Online VCPUs for the domain

More things will be added in the future as we need them.  Or if you want them, we also accept patches.

