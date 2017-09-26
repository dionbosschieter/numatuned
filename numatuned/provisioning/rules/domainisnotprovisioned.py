from numatuned.read import read
from numatuned.virsh import Virsh

class DomainIsNotProvisioned:
    satisfied = True
    def __init__(self, domain):
        virsh = Virsh(domain)
        self.satisfied = virsh.has_numa_assignment() == False
