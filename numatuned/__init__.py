#!/usr/bin/env python3
from .provisioning.provisioningservice import ProvisioningService
from .mappinggenerator import MappingGenerator
from .virsh import Virsh
from .zone import Zone

def fire():
    zonelist = Zone.get_zones()

    if len(zonelist) < 2:
        return print('There are not enough zones to do any kind of balancing, number of zones:', len(zonelist))

    for zone in zonelist:
        print('getting free mem for zone', zone.number, zone.pagesfree())

    domainlist = Virsh.get_domain_list()
    mappinggenerator = MappingGenerator(domainlist, zonelist)
    distribution_list = mappinggenerator.generate()
    provisioning_service = ProvisioningService(zonelist)

    for domain, mapping in distribution_list.items():
        zone = provisioning_service.get_zone_for_domain(domain, mapping)

        if zone == False:
            print('Skipping ', domain)
            continue
        virsh = Virsh(domain)
        virsh.migrate_to(zone)
