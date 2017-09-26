import glob
from subprocess import call
from .read import read

class Virsh:
    """Class can be used to execute virsh commands for a given domain"""
    domain = ""

    def __init__(self, domain):
        self.domain = domain

    @staticmethod
    def get_domain_list():
        pid_files = glob.glob('/var/run/libvirt/qemu/*.pid')
        domain_list = {}
        for pid_file in pid_files:
            # read the pid
            domain_list[pid_file] = read(pid_file)

        return domain_list

    def execute(self, arguments):
        print('virsh', arguments)
        call(['virsh'] + arguments)

    def migrate_to(self, zone):
        self.execute(["numatune",self.domain,"--nodeset", str(zone.number)])
