#!/usr/bin/env python3
import sys
import numatuned

dryrun = False
if len(sys.argv) > 1:
    if sys.argv[1] == '-n':
        dryrun = True

numatuned.fire(60, dryrun)
