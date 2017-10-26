from numatuned.read import read
from numatuned.virsh import Virsh

class DomainIsNotProvisioned:
    def __init__(self, domain):
        self.virsh = Virsh(domain)
    def is_satisfied(self):
        return self.virsh.has_numa_assignment() == False
