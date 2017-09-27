from .rules import *

class ProvisioningService:
    zones = []
    early_abort = 10

    def __init__(self, zones):
        self.zones = zones

    def check_score_for_zone(self, zone, domain, mapping):
        rules = [
            (10, DomainIsNotProvisioned(domain)),
            (10, ZoneHasEnoughSpaceForDomain(zone, mapping)),
            (10, DomainIsRunning(domain)),
            (10, DomainIsNotFresh(domain)),
            (1,  DomainIsAlreadyOnZone(zone, mapping)),
            (1,  ZoneHasMostPagesFree(self.zones, zone)),
        ]
        score = 0
        for bad_score, rule in rules:
            if score == self.early_abort:
                print('Score hit early_abort', domain)
                break
            if rule.satisfied == False:
                print(rule.__class__, 'was not satisfied')
                score = score + bad_score
            else:
                print(rule.__class__, 'was satisfied')

        return score

    def get_zone_for_domain(self, domain, mapping):
        print('Checking provisioning for', domain)
        score_list = []
        for zone in self.zones:
            print('- checking for zone', zone.number, zone.pagesfree())
            score = self.check_score_for_zone(zone, domain, mapping)
            if score < self.early_abort:
                score_list.append((score, zone))

        score_list = sorted(score_list, key=lambda score_zone_list: score_zone_list[0])

        return score_list[0][1] if score_list else False
