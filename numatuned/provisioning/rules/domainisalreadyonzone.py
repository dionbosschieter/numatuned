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
