class DomainIsNotProvisioned:
    satisfied = True
    def __init__(self, domain, mapping):
        total = mapping['total']
        for zone_number, pages in mapping.items():
            if zone_number != 'total' and pages == total:
                self.satisfied = False
                break
