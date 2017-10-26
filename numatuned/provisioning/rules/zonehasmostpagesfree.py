class ZoneHasMostPagesFree:
    def __init__(self, zones, thiszone):
        self.zones = zones
        self.thiszone = thiszone
	def is_satisfied(self):
        for zone in self.zones:
            if zone.number == self.thiszone.number:
                continue
            if self.thiszone.pagesfree() < zone.pagesfree():
                return False
        return True
