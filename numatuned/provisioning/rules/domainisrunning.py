from numatuned.virsh import Virsh

class DomainIsRunning:
    def __init__(self, domain):
        self.virsh = Virsh(domain)
    def is_satisfied(self):
        return self.virsh.is_running()
