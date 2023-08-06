from NagList import NagList
from Base import Base, servicesstatus

from nagparser.Model import Host, ServiceGroup

from nagparser.Services.nicetime import getnicetimefromdatetime

from datetime import datetime


class Nag(Base):
    '''Top level object that 'holds' all the other objects like Services and Hosts.
    The child Nag Objects are defined here so a Host is of type Host.
    '''

    def __init__(self, nag=None):
        super(Nag, self).__init__(nag=nag)

        self.__servicegroups = [None, None]
        self.hosts = None
        self.services = None
        self._servicegroups = None
        self.last_command_check = None
        self.importantservicegroups = None

    name = ''

    @property
    def generated(self):
        return datetime.fromtimestamp(float(self.created))

    @property
    def lastupdated(self):
        return datetime.fromtimestamp(float(self.last_command_check))


    def getstatus(self, onlyimportant=False):
        return servicesstatus(self.getservicegroups(onlyimportant))
    status = property(getstatus)

    def getbadhosts(self):
        return self.getbad(Host)

    def laststatuschange(self, returntimesincenow=True):
        lastchange = max(self.services, key=lambda x: x.laststatuschange(returntimesincenow=False)). \
                        laststatuschange(returntimesincenow=False)

        if returntimesincenow:
            return getnicetimefromdatetime(lastchange)
        else:
            return lastchange

    def getservicegroups(self, onlyimportant=False):

        def _getservicegroups(onlyimportant=onlyimportant):
            if onlyimportant:
                servicegroups = NagList([x for x in self._servicegroups if x.servicegroup_name in self.importantservicegroups])
            else:
                servicegroups = self._servicegroups

                # Build up a servicegroup instance that will have all services NOT in a servicegroup
                noservicegroup = ServiceGroup(self.nag)
                noservicegroup.alias = 'No Service Group'
                noservicegroup.nag = self.nag
                noservicegroup.servicegroup_name = 'noservicegroup'
                noservicegroup.members = ''

                servicesinservicegroup = []
                for servicegroup in self._servicegroups:
                    servicesinservicegroup.extend(servicegroup.services)

                for services in list(set(self.services) - set(servicesinservicegroup)):
                    noservicegroup.members = noservicegroup.members + services.host.host_name + ',' + services.name + ','

                noservicegroup.members = noservicegroup.members.strip(',')
                servicegroups.append(noservicegroup)

                # Build "allservices" sudo servicegroup
                allservicesservicegroup = ServiceGroup(self.nag)
                allservicesservicegroup.alias = 'All Services'
                allservicesservicegroup.nag = self.nag
                allservicesservicegroup.servicegroup_name = 'allservices'
                allservicesservicegroup.members = ''

                for services in self.services:
                    allservicesservicegroup.members = allservicesservicegroup.members + services.host.host_name + ',' + services.name + ','

                allservicesservicegroup.members = allservicesservicegroup.members.strip(',')
                servicegroups.append(allservicesservicegroup)

                servicegroups = NagList(servicegroups)

            return servicegroups

        if onlyimportant and self.__servicegroups[0] is None:
            self.__servicegroups[0] = _getservicegroups(onlyimportant)
        elif not onlyimportant and self.__servicegroups[1] is None:
            self.__servicegroups[1] = _getservicegroups(onlyimportant)

        if onlyimportant:
            return self.__servicegroups[0]
        else:
            return self.__servicegroups[1]

    @property
    def servicegroups(self):
        return self.getservicegroups()

if __name__ == "__main__":
    pass
