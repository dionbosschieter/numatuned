from numatuned.virsh import Virsh

class EntireDomainFitsInZone:
    def __init__(self, domain, zone):
        self.zone = zone
        self.virsh = Virsh(domain)
    def is_satisfied(self):
        return self.virsh.get_memory_in_mb() < self.zone.free_mem_in_mb()
