from datetime import time, timezone, timedelta, datetime, date
from functools import total_ordering
import fetchtimezone


class LagClockError(Exception):
    pass


class LagClock:
    def __init__(self, timezone_):
        self.timezone_ = timezone_

    def __call__(self, awaretime):
        return awaretime.fixed_by(self.timezone_)

    def __getitem__(self, slice_):
        if type(slice_) is not slice:
            raise LagClockError("don't hesitate to use slice as clock!")
        if slice_.stop is None:
            raise LagClockError('no minute data found!')
        return AwareTime(slice_.start, slice_.stop, slice_.step,
                         self.timezone_)


@total_ordering
class AwareTime:
    """
    wrapper of datetime.time (, which is aware)
    """
    def __init__(self, hours, minutes, seconds, timezone_):
        if seconds:
            self.time = time(hour=hours, minute=minutes, second=seconds,
                             tzinfo=timezone_)
        else:
            self.time = time(hour=hours, minute=minutes, tzinfo=timezone_)

    def __eq__(self, other):
        return self.time == other.time

    def __lt__(self, other):
        return self.time < other.time

    def __sub__(self, other):
        return self.time - other.time

    def __repr__(self):
        if self.time.second:
            return self.time.strftime('[%H:%M:%S]')
        else:
            return self.time.strftime('[%H:%M]')

    def utc(self):
        # NOTE: time - timedelta is not allowed!
        utc_dt = datetime.combine(date.today(), self.time) - self.time.utcoffset()
        utctime = utc_dt.time()
        # NOTE: fix inner timedelta (timezone in utctime is NOT IN UTC)
        return AwareTime(utctime.hour, utctime.minute, utctime.second,
                         timezone(timedelta(hours=0)))

    def fixed_by(self, timezone_):
        # convert self.time to utc
        utc = self.utc()
        # NOTE: time + timedelta is not allowed!
        # convert utc to timezone_
        fixed_dt = datetime.combine(date.today(), utc.time) + timezone_.utcoffset(None)
        fixedtime = fixed_dt.time()
        # NOTE: fix inner timedelta (timezone in fixedtime is NOT FIXED)
        return AwareTime(fixedtime.hour, fixedtime.minute, fixedtime.second,
                         timezone_)
