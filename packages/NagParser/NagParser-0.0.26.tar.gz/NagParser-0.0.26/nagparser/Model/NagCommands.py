import time
import os

from datetime import datetime

from nagparser.Services.nicetime import getdatetimefromnicetime


class NagCommands(object):
    def __init__(self, nag):
        self.nag = nag

    def scheduledowntime(self, author, starttime, endtime, comment, apikey='default', doappend=False):
        TIMEFORMAT = '%Y%m%d%H%M'
        try:
            start = int(time.mktime(time.strptime(starttime, TIMEFORMAT)))
        except Exception:
            try:
                start = int(time.mktime(getdatetimefromnicetime(starttime).timetuple()))
            except Exception:
                return 'Error: "StartTime" not in correct format.'
        try:
            end = int(time.mktime(time.strptime(endtime, TIMEFORMAT)))
        except Exception:
            try:
                end = int(time.mktime(getdatetimefromnicetime(endtime, datetime.fromtimestamp(start)).timetuple()))
            except Exception:
                return 'Error: "EndTime" not in correct format.'

        values = {'fixed': 1, 'trigger_id': 0, 'duration': 0, 'author': author,
                  'start_time': start, 'end_time': end, 'comment': comment}

        if self.nag.classname() == 'servicegroup':
            values['servicegroup_name'] = self.nag.servicegroup_name
            command = 'SCHEDULE_SERVICEGROUP_SVC_DOWNTIME;<servicegroup_name>;<start_time>;<end_time>;<fixed>;<trigger_id>;<duration>;<author>;<comment>'
        elif self.nag.classname() == 'host':
            values['host_name'] = self.nag.host_name
            command = 'SCHEDULE_HOST_SVC_DOWNTIME;<host_name>;<start_time>;<end_time>;<fixed>;<trigger_id>;<duration>;<author>;<comment>'
        elif self.nag.classname() == 'service':
            values['host_name'] = self.nag.host_name
            values['service_description'] = self.nag.service_description
            command = 'SCHEDULE_SVC_DOWNTIME;<host_name>;<service_description>;<start_time>;<end_time>;<fixed>;<trigger_id>;<duration>;<author>;<comment>'
        else:
            return 'Error: Invalid Nag object'

        for value in values:
            command = command.replace('<' + value + '>', str(values[value]))

        if command.find('<') > 0:
            return 'Error: Incomplete Nagios command file format substitution '

        command = '[' + str(int(time.time())) + '] ' + command

        if doappend:
            try:
                if not self.nag.nag.config.getpermissions(apikey):
                    return 'Error: Invalid or Missing API Key.  A valid API Key is required.'
                else:
                    commandfile = os.open(self.nag.nag.config.NAGIOS_CMD_FILE, os.O_RDWR | os.O_NONBLOCK)
                    os.write(commandfile, command + '\n')
                    os.close(commandfile)
            except Exception, e:
                print e
                return 'Error: Appending to the Nagios command file'

        return command
