class DomainIsNotFresh:
    satisfied = False
    def __init__(self, domain):
        domain = Virsh(domain)
        pid = domain.get_pid()
        # todo
