from datetime import datetime, timedelta
from string import find


def getnicetimefromdatetime(datetimeinput, basedatetime=None):
    if basedatetime is None:
        base = datetime.now()
    else:
        base = basedatetime

    if (base > datetimeinput):
        delta = base - datetimeinput
    else:
        delta = datetimeinput - base

    hours, remainder = divmod(delta.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    if delta.days > 0:
        result = ' %sd  %sh' % (delta.days, hours)
    elif hours > 0:
        result = '%sh %sm' % (hours, minutes)
    elif minutes > 0:
        result = '%sm %ss' % (minutes, seconds)
    else:
        result = '%ss' % (seconds)

    return result


def getdatetimefromnicetime(nicetime, basedatetime=None):
    if basedatetime is None:
        base = datetime.now()
    else:
        base = basedatetime

    result = [0, 0, 0, 0]
    sections = nicetime.lower().split(':')
    if len(sections) == 1:
        sections = nicetime.split(' ')

    for section in sections:
        if find(section, 'd') > 0:
            result[0] = int(section.replace('d', ''))
        if find(section, 'h') > 0:
            result[1] = int(section.replace('h', ''))
        if find(section, 'm') > 0:
            result[2] = int(section.replace('m', ''))
        if find(section, 's') > 0:
            result[3] = int(section.replace('s', ''))

    delta = timedelta(days=result[0], hours=result[1], minutes=result[2], seconds=result[3])

    return base + delta

if __name__ == "__main__":
    pass
