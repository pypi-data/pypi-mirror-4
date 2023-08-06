from NagList import NagList
from Base import Base, servicesstatus

from nagparser.Services.nicetime import getnicetimefromdatetime


class ServiceGroup(Base):
    '''ServiceGroup represents a service group definition found in objects.cache.'''

    def __init__(self, nag):
        super(ServiceGroup, self).__init__(nag=nag)

        self._hostsandservices = None
        self.members = None
        self.alias = None

    def gethostsandservices(self):
        def _gethostsandservices():
            tempservices = []
            temphosts = []
            if self.members is not None and self.members != '':
                members = self.members.split(',')
                for i in range(len(members)):
                    if i % 2 == 0:
                        host = self.nag.gethost(members[i])
                        if host is not None:
                            temphosts.append(host)
                            service = host.getservice(members[i + 1])
                            if service is not None:
                                tempservices.append(service)

            return (list(set(tempservices)), list(set(temphosts)))
        if self._hostsandservices == None:
            self._hostsandservices = _gethostsandservices()

        return self._hostsandservices

    @property
    def services(self):
        return NagList(self.gethostsandservices()[0])

    @property
    def hosts(self):
        return NagList(self.gethostsandservices()[1])

    @property
    def name(self):
        return self.alias

    def getstatus(self, *arg):
        return servicesstatus(self.services)
    status = property(getstatus)

    def laststatuschange(self, returntimesincenow=True):
        lastchange = max(self.services, key=lambda x: x.laststatuschange(returntimesincenow=False)). \
                        laststatuschange(returntimesincenow=False)

        if returntimesincenow:
            return getnicetimefromdatetime(lastchange)
        else:
            return lastchange
