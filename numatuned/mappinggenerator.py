from .read import read

class MappingGenerator:
    """This class is used to generate a hashmap with libvirt domainobjects and amount of mem on each zone"""

    def __init__(self, domains, zones):
        self.domains = domains
        self.zones = zones

    def generate(self):
        distribution_list = {}
        for pid_file, pid in self.domains.items():
            domain = self.get_domain_from_pid_file(pid_file)
            distribution_list[domain] = self.get_numa_mapping_for_pid(pid)

        return distribution_list

    def get_domain_from_pid_file(self, pid_file):
        basename = pid_file.split('/')[-1]
        return basename.replace('.pid','')

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
