#!/usr/bin/env python3
import glob

def read(path_to_file):
    """
    Open the file, read it, and close the file.
    """
    with open(path_to_file, mode='r') as f:
        return f.read()

class Zone:
    """Zone value object"""
    number = 0

    def __init__(self, zone_number):
        self.number = int(zone_number)

    def get_node_kernel_path(self):
        return "/sys/devices/system/node/node{}".format(self.number)

    def get_zone_key(self):
        return "N{}".format(self.number)

    def get_vmstat(self):
        vmstat = read(self.get_node_kernel_path() + "/vmstat")
        vmstat_list = {}
        for line in vmstat.split('\n'):
            line_data = line.split(' ')
            if len(line_data) != 2:
                continue
            vmstat_list[line_data[0]] = line_data[1]

        return vmstat_list

    def pagesfree(self):
        vmstat = self.get_vmstat()
        return vmstat['nr_free_pages']

    def get_cpu_list(self):
        return read(self.get_node_kernel_path() + "/cpulist")

    @staticmethod
    def get_zones():
        available_zones = read("/sys/devices/system/node/online")
        zones = []
        for zone_number in available_zones.split('-'):
            zones.append(Zone(zone_number))
        return zones

class Main:
    """This class is used to generate a hashmap with libvirt domainobjects and amount of mem on each"""

    def __init__(self, domains, zones):
        self.domains = domains
        self.zones = zones

    def generate_distribution(self):
        distribution_list = {}
        for domain, pid in self.domains.items():
            uniq_key = domain + '_' + pid
            distribution_list[uniq_key] = self.get_numa_mapping_for_pid(pid)

        return distribution_list

    def get_numa_mapping_for_pid(self,pid):
        mapping = read("/proc/{}/numa_maps".format(pid))
        pid_mapping = {}

        # init pid_mapping
        for zone in self.zones:
            pid_mapping[zone.number] = 0

        for line in mapping.split('\n'):
            line_struct = self.get_mapping_struct_from_line(line)
            if ('kernelpagesize_kB' in line_struct) == False:
                continue # skip if no pages
            pagesize = int(line_struct['kernelpagesize_kB'])

            # get pages foreach numa zone
            for zone in self.zones:
                if zone.get_zone_key() in line_struct:
                    num_pages = int(line_struct[zone.get_zone_key()])
                    pages_in_kb = num_pages * pagesize
                    pid_mapping[zone.number] = pid_mapping[zone.number] + pages_in_kb

        return pid_mapping

    def get_mapping_struct_from_line(self, line):
        line_dict = {}

        for key in line.split(' '):
            data = key.split('=')
            if len(data) != 2:
                continue
            line_dict[data[0]] = data[1]

        return line_dict

def get_domain_list():
    pid_files = glob.glob('/var/run/libvirt/qemu/*.pid')
    domain_list = {}
    for pid_file in pid_files:
        # read the pid
        domain_list[pid_file] = read(pid_file)

    return domain_list

zonelist = Zone.get_zones()
domainlist = get_domain_list()
distribution = Main(domainlist, zonelist)

for zone in zonelist:
    print('getting free mem for zone', zone.number, zone.pagesfree())

# keep an inmem status of what not to move
# so if we change the zone distribution algorithm
# we can start over without sticking to the current numatune__nodeset
already_done = []
distribution_list = distribution.generate_distribution()

# TODO: build class ProvisioningService
provisioning_service = ProvisioningService(zonelist)

# TODO: build sorting method
sorted_domains = provisioning_service.sort_domain_list(distribution_list)

for domain, mapping in sorted_domains.items():
    print('Checking', domain)
    if provisioning_service.should_skip(domain):
        print('Skipping ', domain)
        continue

    zone = provisioning_service.get_zone_for_domain(domain, mapping)

    virsh = Virsh(domain)

    # todo: implement
    virsh.migrate_to(zone)

    total = 0
    for zone_number,pages in mapping.items():
        total = total + pages
    print('- total pages ', total)

    # percentual calculation
    preferred_zone = False
    for zone in zonelist:
        pages_on_zone = mapping[zone.number]
        percent = (100 / total) * pages_on_zone
        print('- percent ', percent, 'on zone', zone.number)
        if percent > 75:
            preferred_zone = zone
            print ('-- most pages are on zone',zone.number)

    already_done.append(domain)
