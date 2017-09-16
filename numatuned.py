#!/usr/bin/env python3

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

zonelist = Zone.get_zones()

for zone in zonelist:
    print('getting free mem for zone', zone.number)
    print(zone.pagesfree())
