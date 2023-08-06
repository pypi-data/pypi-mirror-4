from NagCommands import NagCommands
from NagList import NagList
from NagConfig import NagConfig

import time
from datetime import datetime

import types

import json


class Base(object):
    '''This is the base class that other core objects inherit.  This class defines common functions and should not be directly instantiated. '''
    def getnowtimestamp(self):
        return time.time()

    def __init__(self, nag=None):
        if nag == None:
            self.nag = self
            self._nagcreated = datetime.now()
        else:
            self.nag = nag

    @property
    def commands(self):
        return NagCommands(self)

    @property
    def attributes(self):
        '''Returns a list of tuples with each tuple representing an attribute'''

        output = []
        for attr in self.__dict__:
            attrtype = type(self.__dict__[attr])
            if attrtype is not types.ListType and attrtype is not NagList and attrtype is not NagConfig \
                and attrtype is not tuple and not issubclass(attrtype, Base) and not attr == '_nagcreated':
                output.append((attr, self.__dict__[attr]))

        return output

    def getbad(self, objtype=None, items=None):
        if objtype is None and items is None:
            raise Exception("objtype or items must be passed")

        if items == None:
            items = getattr(self, self.classname(objtype) + 's')
        else:
            return NagList([x for x in items if x.status[0] != 'ok'])

    def getbadservices(self):
        return self.getbad(items=self.services)

    def classname(self, classname=None):
        if classname:
            classbase = classname
        else:
            classbase = self.__class__

        parts = str(classbase).split("'")[1].lower().split('.')
        return parts[len(parts) - 1]

    def genoutput(self, outputformat='json', items=None, finaloutput=True):
        outputformat = outputformat.lower()

        #Setup
        output = {}
        if outputformat == 'json':
            output['objtype'] = self.classname()
            output['attributes'] = {}
        else:
            return 'Invalid Output'

        #Attributes
        for attr in self.attributes:
            output['attributes'][attr[0]] = attr[1]

        order = ['host', 'service', 'servicegroup']
        if items is None:
            if order[0] == self.classname():
                items = getattr(self, order[1] + 's')
            else:
                try:
                    items = getattr(self, order[0] + 's')
                except Exception:
                    items = []

        for obj in items:
            temp = obj.genoutput(outputformat=outputformat, finaloutput=False)
            if outputformat == 'json':
                if obj.classname() + 's' not in output.keys():
                    output[obj.classname() + 's'] = []
                output[obj.classname() + 's'].append(temp)

        if outputformat == 'json' and finaloutput:
            output = json.dumps(output)

        return output

    def getservice(self, service_description):
        try:
            return getattr(self.services, service_description)
        except AttributeError:
            return None

    def gethost(self, host_name):
        try:
            return getattr(self.hosts, host_name)
        except AttributeError:
            return None

    def getservicegroup(self, servicegroup_name):
        try:
            return [x for x in self.nag.getservicegroups() if x.__dict__['servicegroup_name'] == servicegroup_name][0]
        except Exception:
            return None


def servicesstatus(services):
    hasdowntime = max([x.status[1] for x in services])
    if len([x for x in services if x.status[0] == 'stale']):
        return 'unknown', hasdowntime

    if len([x for x in services if x.status[0] == 'critical' and x.status[1] == False]):
        return 'critical', hasdowntime

    elif len([x for x in services if x.status[0] == 'warning' and x.status[1] == False]):
        return 'warning', hasdowntime

    elif len([x for x in services if x.status[0] == 'ok' and x.status[1] == True]):
        return 'downtime', hasdowntime

    elif len([x for x in services if x.status[0] == 'unknown' or x.status[0] == 'stale']):
        return 'unknown', hasdowntime
    else:
        return 'ok', hasdowntime
