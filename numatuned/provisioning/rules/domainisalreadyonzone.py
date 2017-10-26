class DomainIsAlreadyOnZone:
    def __init__(self, zone, mapping):
        self.zone = zone
        self.mapping = mapping
    def is_satisfied(self):
        items = self.mapping.items()
        zone_numa_mapping = sorted(items, key=lambda numamap: numamap[1], reverse=True)
        # zone equals zone with most pages of domain
        for zone_key, pages in zone_numa_mapping:
            if zone_key == 'total':
                continue
            return self.zone.number == zone_key
