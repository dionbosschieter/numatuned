#!/usr/bin/env python3
import glob

def read(path_to_file):
    """
    Open the file, read it, and close the file.
    """
    with open(path_to_file, mode='r') as f:
        return f.read()

class DomainIsNotProvisioned:
    satisfied = True
    def __init__(self, domain, mapping):
        total = mapping['total']
        for zone_number, pages in mapping.items():
            if zone_number != 'total' and pages == total:
                self.satisfied = False
                break

class ZoneHasEnoughSpaceForDomain:
    satisfied = False
    def __init__(self, zone, mapping):
        self.satisfied = zone.pagesfree() > mapping['total']

class DomainIsAlreadyOnZone:
    satisfied = False
    def __init__(self, zone, mapping):
        zone_numa_mapping = sorted(mapping.items(), key=lambda numamap: numamap[1], reverse=True)
        # zone equals zone with most pages of domain
        for zone_key, pages in zone_numa_mapping:
            if zone_key == 'total':
                continue
            self.satisfied = zone.number == zone_key
            break

class ZoneHasMostPagesFree:
    satisfied = True
    def __init__(self, zones, thiszone):
        for zone in zones:
            if zone.number == thiszone.number:
                continue
            if thiszone.pagesfree() < zone.pagesfree():
                self.satisfied = False

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
        return int(vmstat['nr_free_pages'])

    def get_cpu_list(self):
        return read(self.get_node_kernel_path() + "/cpulist")

    @staticmethod
    def get_zones():
        available_zones = read("/sys/devices/system/node/online")
        zones = []
        for zone_number in available_zones.split('-'):
            zones.append(Zone(zone_number))
        return zones

class MappingGenerator:
    """This class is used to generate a hashmap with libvirt domainobjects and amount of mem on each zone"""

    def __init__(self, domains, zones):
        self.domains = domains
        self.zones = zones

    def generate(self):
        distribution_list = {}
        for domain, pid in self.domains.items():
            uniq_key = domain + '_' + pid
            distribution_list[uniq_key] = self.get_numa_mapping_for_pid(pid)

        return distribution_list

    def get_numa_mapping_for_pid(self,pid):
        mapping = read("/proc/{}/numa_maps".format(pid))
        pid_mapping = {'total':0}

        # init pid_mapping
        for zone in self.zones:
            pid_mapping[zone.number] = 0

        for line in mapping.split('\n'):
            line_struct = self.get_mapping_struct_from_line(line)
            if ('kernelpagesize_kB' in line_struct) == False:
                continue # skip if no pages

            # get pages foreach numa zone
            for zone in self.zones:
                if zone.get_zone_key() in line_struct:
                    num_pages = int(line_struct[zone.get_zone_key()])
                    pid_mapping[zone.number] = pid_mapping[zone.number] + num_pages
                    pid_mapping['total'] = pid_mapping['total'] + num_pages

        return pid_mapping

    def get_mapping_struct_from_line(self, line):
        line_dict = {}

        for key in line.split(' '):
            data = key.split('=')
            if len(data) != 2:
                continue
            line_dict[data[0]] = data[1]

        return line_dict

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

    def execute(self, command):
        print(command)
        return True # TODO: implement

    def migrate_to(self, zone):
        self.execute("numatune {} --setnode {}".format(self.domain, zone.number))

zonelist = Zone.get_zones()

for zone in zonelist:
    print('getting free mem for zone', zone.number, zone.pagesfree())

# keep an inmem status of what not to move
# so if we change the zone distribution algorithm
# we can start over without sticking to the current numatune__nodeset
class ProvisioningService:
    zones = []
    early_abort = 10

    def __init__(self, zones):
        self.zones = zones

    def check_score_for_zone(self, zone, domain, mapping):
        rules = [
            (10, DomainIsNotProvisioned(domain, mapping)),
            (10, ZoneHasEnoughSpaceForDomain(zone, mapping)),
            (1,  DomainIsAlreadyOnZone(zone, mapping)),
            (1,  ZoneHasMostPagesFree(self.zones, zone)),
        ]
        score = 0
        for bad_score, rule in rules:
            if score == self.early_abort:
                print('Score hit early_abort', domain)
                break
            if rule.satisfied == False:
                print(rule.__class__, 'was not satisfied')
                score = score + bad_score
            else:
                print(rule.__class__, 'was satisfied')

        return score

    def get_zone_for_domain(self, domain, mapping):
        print('Checking provisioning for', domain)
        score_list = []
        for zone in self.zones:
            print('- checking for zone', zone.number, zone.pagesfree())
            score = self.check_score_for_zone(zone, domain, mapping)
            if score < self.early_abort:
                score_list.append((score, zone))

        score_list = sorted(score_list, key=lambda score_zone_list: score_zone_list[0])

        return score_list[0][1] if score_list else False

domainlist = Virsh.get_domain_list()
mappinggenerator = MappingGenerator(domainlist, zonelist)
distribution_list = mappinggenerator.generate()

# TODO: build class ProvisioningService
provisioning_service = ProvisioningService(zonelist)

for domain, mapping in distribution_list.items():
    zone = provisioning_service.get_zone_for_domain(domain, mapping)

    if zone == False:
        print('Skipping ', domain)
        continue
    virsh = Virsh(domain)
    virsh.migrate_to(zone)
