import os
import time
from numatuned.virsh import Virsh

class DomainIsNotFresh:
    def __init__(self, domain):
        self.domain = domain

    def is_satisfied(self):
        domain = Virsh(self.domain)
        pidfile = domain.get_pid_file()
        mtime = os.path.getmtime(pidfile)
        now = time.time()
        return now - 120 > mtime # domain is 2 minutes old
