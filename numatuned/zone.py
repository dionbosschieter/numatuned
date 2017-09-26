from .read import read

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
