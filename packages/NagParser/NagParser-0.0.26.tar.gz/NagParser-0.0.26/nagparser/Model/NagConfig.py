import os
import types


class NagConfig(object):
    def __init__(self, files):
        self.STALE_THRESHOLD = 240
        self.IGNORE_STALE_DATA = False
        self.NAGIOS_CMD_FILE = '/var/lib/nagios3/rw/nagios.cmd'
        self.IMPORTANTSERVICEGROUPS = {}
        self.basicAPIKEYS = []
        self.DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S'
        self.REQUIRE_HARD_SERVICE_STATUS = False

        allfilesexist = True
        for temp in files:
            if not os.path.exists(temp):
                allfilesexist = False

        if allfilesexist:
            self.files = files
        else:
            raise IOError('File(s) not found')

    def _get_basicapikeys(self):
        return self.basicAPIKEYS

    def _set_basicapikeys(self, apikeys):
        if type(apikeys) is not types.ListType:
            apikeys = [apikeys]
        self.basicAPIKEYS = apikeys

    APIKEYS = property(_get_basicapikeys, _set_basicapikeys)


    def getpermissions(self, apikey):
        '''Basic apikey check function. Can be overridden to provide custody apikey validation functionality.
            Should return a list of permissions or an empty list of no permissions.
            Permissions are currently un-utilized but future versions of the NagCommands() will use them to
            restrict access etc...'''

        if apikey in self.basicAPIKEYS:
            return ['access granted']
        else:
            return []
