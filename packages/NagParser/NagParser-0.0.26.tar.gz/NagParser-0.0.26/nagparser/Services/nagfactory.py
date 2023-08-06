#!/usr/bin/env python

import re

from nagparser.Model.NagList import NagList
from nagparser.Model import Nag, Host, Service, ServiceGroup


def parse(config):
    tempobjs = []
    files = config.files
    importantservicegroups = config.IMPORTANTSERVICEGROUPS

    nag = None
    for filename in files:
        tempfile = open(filename)
        content = tempfile.read()
        tempfile.close()

        if nag == None:
            nag = Nag()
        if '.cache' in filename:
            sectionsnames = ['define servicegroup']
        elif '.dat' in filename:
            sectionsnames = ['hoststatus', 'servicestatus', 'programstatus', 'info']
        else:
            raise Exception('Invalid filename detected')

        for section in sectionsnames:
            pat = re.compile(section + ' \{([\S\s]*?)\}', re.DOTALL)

            for sectioncontent in pat.findall(content):
                if section == 'hoststatus':
                    temp = Host(nag)
                elif section == 'servicestatus':
                    temp = Service(nag)
                elif section in ['programstatus', 'info']:
                    temp = nag
                elif section == 'define servicegroup':
                    temp = ServiceGroup(nag)

                for attr in sectioncontent.splitlines():
                    attr = attr.strip()
                    if len(attr) == 0 or attr.startswith('#'):
                        pass
                    else:
                        if section == 'define servicegroup':
                            delim = '\t'
                        else:
                            delim = '='

                        shortattr = attr.split(delim)[0].lower()
                        value = attr.replace(shortattr + delim, '')
                        try:
                            value = int(str(value))
                        except ValueError:
                            try:
                                value = float(str(value))
                            except ValueError:
                                pass

                        temp.__dict__[shortattr] = value
                tempobjs.append(temp)

    hosts = [x for x in tempobjs if isinstance(x, Host)]
    services = [x for x in tempobjs if isinstance(x, Service)]
    servicegroups = [x for x in tempobjs if isinstance(x, ServiceGroup)]

    nag.importantservicegroups = importantservicegroups
    nag.config = config

    if len(hosts):
        nag.hosts = NagList(hosts)
    if len(services):
        nag.services = NagList(services)
    if len(servicegroups):
        nag._servicegroups = NagList(servicegroups)

    return nag


if __name__ == "__main__":
    pass
