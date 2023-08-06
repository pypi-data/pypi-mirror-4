from NagList import NagList
from Base import Base

from nagparser.Services.nicetime import getnicetimefromdatetime

import time
from datetime import datetime


class Service(Base):
    '''Service represents a service definition found in status.dat'''

    def __init__(self, nag):
        super(Service, self).__init__(nag=nag)

        self.host_name = None
        self.last_state_change = None
        self.service_description = None
        self.active_checks_enabled = None
        self.current_state = None
        self.next_check = None
        self.scheduled_downtime_depth = None
        self.state_type = None

    @property
    def host(self):
        # pylint: disable=E1103
        return NagList([x for x in self.nag.hosts if x.host_name == self.host_name]).first

    @property
    def name(self):
        return self.service_description

    def getstatus(self, *arg):
        isdowntime = False
        if int(self.scheduled_downtime_depth) > 0:
            isdowntime = True
        # pylint: disable=E1103
        if ((time.time() - self.nag.config.STALE_THRESHOLD) > int(self.next_check) and
            self.active_checks_enabled == 1 and
            self.nag.config.IGNORE_STALE_DATA == False):
            return 'stale', isdowntime

        if self.nag.config.REQUIRE_HARD_SERVICE_STATUS and int(self.state_type) != 1:
            return 'ok', isdowntime
        if int(self.current_state) == 2:
            return 'critical', isdowntime
        elif int(self.current_state) == 1:
            return 'warning', isdowntime
        elif int(self.current_state) > 2 or int(self.current_state) < 0:
            return 'unknown', isdowntime
        else:
            return 'ok', isdowntime
    status = property(getstatus)

    def laststatuschange(self, returntimesincenow=True, timestamp=None):
        if timestamp:
            lastchange = datetime.fromtimestamp(float(timestamp))
        else:
            lastchange = datetime.fromtimestamp(float(self.last_state_change))

        if returntimesincenow:
            return getnicetimefromdatetime(lastchange)
        else:
            return lastchange

    @property
    def servicegroups(self):
        servicegroups = []
        # pylint: disable=E1103
        for servicegroup in self.nag.getservicegroups():
            if self in servicegroup.services:
                servicegroups.append(servicegroup)
        return NagList(servicegroups)
