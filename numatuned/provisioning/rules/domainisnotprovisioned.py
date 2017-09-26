from numatuned.read import read
from numatuned.virsh import Virsh

class DomainIsNotProvisioned:
    satisfied = True
    def __init__(self, domain, mapping):
        virsh = Virsh(domain)
        satisfied = virsh.has_numa_assignment()
