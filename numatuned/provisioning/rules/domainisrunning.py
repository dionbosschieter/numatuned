from numatuned.virsh import virsh

class DomainIsRunning:
    satisfied = False
    def __init__(self, domain):
        virsh = Virsh(domain)
        satisfied = virsh.is_running()
