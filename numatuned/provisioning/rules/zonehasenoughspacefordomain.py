class ZoneHasEnoughSpaceForDomain:
    satisfied = False
    def __init__(self, zone, mapping):
        self.satisfied = zone.pagesfree() > mapping['total']
