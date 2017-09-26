import glob
import subprocess
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
        output = subprocess.check_output(["virsh"] + arguments, stderr=subprocess.STDOUT)
        return output.decode('utf-8')

    def migrate_to(self, zone):
        self.execute(["numatune", self.domain, "--nodeset", str(zone.number)])

    def has_numa_assignment(self):
        output = self.execute(["numatune", self.domain])
        for line in output.split('\n'):
            exploded = line.split(':')
            key = exploded[0].strip(' ')
            if key == 'numa_nodeset':
                value = exploded[1].strip(' ')
                if value != '':
                    return True
        return False

    def is_running(self):
        output = self.execute(["domstate", self.domain])
        domstate = output.strip('\n').strip(' ').strip('\n')
        return domstate == 'running'

    def get_pid(self):
        pid = read('/var/run/libvirt/qemu/' + self.domain + '.pid')
        return pid
