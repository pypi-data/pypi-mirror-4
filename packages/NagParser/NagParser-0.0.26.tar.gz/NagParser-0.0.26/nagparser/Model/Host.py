from Base import Base, servicesstatus
from NagList import NagList

from nagparser.Services.nicetime import getnicetimefromdatetime


class Host(Base):
    '''Host represents a host definition found in status.dat.'''

    def __init__(self, nag):
        super(Host, self).__init__(nag=nag)
        self.host_name = ''

    @property
    def services(self):
        # pylint: disable=E1103
        return NagList([x for x in self.nag.services if x.host_name == self.host_name])

    @property
    def name(self):
        return self.host_name

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
