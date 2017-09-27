import os
import time
from numatuned.virsh import Virsh

class DomainIsNotFresh:
    satisfied = False
    def __init__(self, domain):
        domain = Virsh(domain)
        pidfile = domain.get_pid_file()
        # todo
        mtime = os.path.getmtime(pidfile)
        now = time.time()
        # domain is 5 minutes old
        if now - 300 > mtime:
            self.satisfied = True
