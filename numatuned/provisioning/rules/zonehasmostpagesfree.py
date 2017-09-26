class ZoneHasMostPagesFree:
    satisfied = True
    def __init__(self, zones, thiszone):
        for zone in zones:
            if zone.number == thiszone.number:
                continue
            if thiszone.pagesfree() < zone.pagesfree():
                self.satisfied = False
