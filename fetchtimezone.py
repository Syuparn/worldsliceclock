import re
from datetime import timedelta, timezone
import subprocess
import more_itertools


def powershell_in_eng(func):
    """
    decorator to set PowerShell English mode (set back again when inner func
    finished)
    """
    def _wrapper(*args, **kwargs):
        subprocess.call('chcp 437', shell=True)
        retval = func(*args, **kwargs)
        subprocess.call('chcp 932', shell=True)
        return retval
    return _wrapper


def parse_timezone_lines(tz_lines):
    # tz_lines
    # = ['(UTC+-hh:mm) place1, place2...', '(timezone) Standard Time', '']
    line1pattern = re.compile(r'\(UTC([\+-]\d\d):(\d\d)\) (.*)')
    line2pattern = re.compile(r'(.+?) Standard Time')
    hours = int(line1pattern.sub(r'\1', tz_lines[0]))
    minutes = int(line1pattern.sub(r'\2', tz_lines[0]))
    cities = line1pattern.sub(r'\3', tz_lines[0]).strip().split(',')
    country = line2pattern.sub(r'\1', tz_lines[1])
    lower_snake = lambda s: re.sub(r'( |\W)+', '_', s.strip().lower())
    places = {lower_snake(place) for place in set(cities + [country])}
    return hours, minutes, places


@powershell_in_eng
def fetch_timezones():
    """
    timezone data {'place name': timedelta} fetched from PowerShell tzutil
    """
    # fetch timezone data from tzutil
    p = subprocess.Popen('tzutil /l', shell=True, stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE)
    stdout_data, stderr_data = p.communicate()
    timezone_lines = stdout_data.decode('cp437').split('\r\n')
    # timezone_lines: each 3 lines describes a timezone
    timezone_ = {}
    for chunked_timezone_lines in more_itertools.chunked(timezone_lines, 3):
        if len(chunked_timezone_lines) < 3:
            continue
        if chunked_timezone_lines[1] == 'UTC':
            continue # because format is different
        hour, min, place_names = parse_timezone_lines(chunked_timezone_lines)
        timezone_.update({name: {'hours': hour, 'minutes': min}
                          for name in place_names})
    return timezone_


if __name__ == '__main__':
    timezones = fetch_timezones()

    # generate script of sliceclock instance
    import_lines = ['from sliceclock import LagClock',
                    'from datetime import timedelta, timezone']
    instance_lines =\
        [f'{k} = LagClock(timezone(timedelta(hours={v["hours"]}, minutes={v["minutes"]})))'
         for k, v in timezones.items()]
    code_lines = import_lines + instance_lines

    with open('worldclock.py', 'w') as f:
        f.write('\n'.join(code_lines))
