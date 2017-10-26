class ZoneHasEnoughSpaceForDomain:
    satisfied = False
    def __init__(self, zone, mapping):
        self.zone = zone
        self.mapping = mapping
	def is_satisfied(self):
        return self.zone.pagesfree() > self.mapping['total']
