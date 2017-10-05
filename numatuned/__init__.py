#!/usr/bin/env python3
import time
import signal

from .provisioning import ProvisioningService
from .mappinggenerator import MappingGenerator
from .virsh import Virsh
from .zone import Zone
from .signalcatcher import SignalCatcher

def fire(scansleep, dryrun=False):
    """Fires the application of, stays in a loop checking for
    zone balancing every scansleep seconds"""
    migated_domains = []
    while True:
        zonelist = Zone.get_zones()
        signalcatcher = SignalCatcher()

        if dryrun:
            print('Dryrun is enabled')

        if len(zonelist) < 2:
            print('There are not enough zones to do balancing, num of zones:', len(zonelist))
            return

        for zone in zonelist:
            print('getting free mem for zone', zone.number, zone.pagesfree())

        migrated_domains = run(zonelist, dryrun, migrated_domains)

        if dryrun:
            print('Stopping loop as we are dry running')
            break

        for i in range(0, scansleep):
            time.sleep(1)
            if signalcatcher.kill_now:
                print('Stopping...', i)
                return

def run(zonelist, dryrun, migrated_domains):
    """Creates a domain list with a mapping on each zone
    then migrates if the ProvisioningService returns a zone"""
    domainlist = Virsh.get_domain_list()
    mappinggenerator = MappingGenerator(domainlist, zonelist)
    distribution_list = mappinggenerator.generate()
    provisioning_service = ProvisioningService(zonelist)

    for domain, mapping in distribution_list.items():
        virsh = Virsh(domain)
        if virsh.get_pid() in migrated_domains:
            continue
        zone = provisioning_service.get_zone_for_domain(domain, mapping)

        if zone is False:
            print('Skipping ', domain)
            continue
        print('Migrating', domain, 'to', zone.number)
        migrated_domains.append(virsh.get_pid())
        if dryrun is False:
            virsh.migrate_to(zone)
    return migrated_domains
