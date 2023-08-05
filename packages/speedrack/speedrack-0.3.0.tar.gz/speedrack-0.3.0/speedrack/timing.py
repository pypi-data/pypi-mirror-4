import re

_timeparse = re.compile(r'((?P<months>\d+)M)?((?P<weeks>\d+)w)?((?P<days>\d+)d)?((?P<hours>\d+)h)?((?P<minutes>\d+)m)?((?P<seconds>\d+)s)?')
def parse_interval(time_string):
    ''' converts simple time string to interval format used by
    apscheduler, e.g. "3m30s" becomes:
    { 'seconds': 30, 'minutes': 3, 'hours': None, 'weeks': None, ... }
    '''
    if not time_string:
        return None
    result = _timeparse.match(time_string)
    if not result:
        return None
    answer = {}
    for k,v in result.groupdict().items():
        if not v:
            continue
        answer[k] = int(v)
    return answer

_allowed_keys = ['second', 'minute', 'hour', 'day_of_week', 'week', 'day', 'month', 'year']
def parse_cron(cron):
    ''' Returns a dict() suitable for passing to
    scheduler.add_cron_job(), or False if a configuration error'''

    if not cron:
        return None

    unknown = [x for x in cron.keys() if x not in _allowed_keys]
    if unknown:
        return False

    return cron
