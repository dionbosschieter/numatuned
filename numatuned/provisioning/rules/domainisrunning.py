from numatuned.virsh import Virsh

class DomainIsRunning:
    satisfied = False
    def __init__(self, domain):
        virsh = Virsh(domain)
        self.satisfied = virsh.is_running()