'''
crontab_micropython.py

MicroPython port of crontab.py by Josiah Carlson.
Original Copyright 2011-2025 Josiah Carlson
Released under the GNU LGPL v2.1 and v3

Ported for MicroPython, removing datetime, timedelta, and other
dependencies not available in standard MicroPython.
Uses time.mktime() and time.localtime() for date calculations.

*** Modified to use custom 'power_manager' as time source. ***
'''

from ucollections import namedtuple # MicroPython replacement
import time
from modules import utils

# --- MODIFICATION: Import and create PowerManager instance ---
try:
    from modules import power_manager
    # Create a global instance to reuse it
    _pm_instance = power_manager.PowerManager()
    utils.log_info("PowerManager loaded.")
except ImportError:
    utils.log_error("Could not load power_manager, falling back to time.time().")
    _pm_instance = None
# --- END OF MODIFICATION ---


# --- MicroPython replacements for datetime/timedelta ---
# We use Unix timestamps (seconds since epoch) as the base.
# time.time() in MicroPython (if RTC is set) returns seconds since 1970-01-01.

SECOND = 1
MINUTE = 60
HOUR = 3600
DAY = 86400
WEEK = 604800
# Approximations used by original logic for month/year steps
_MONTH_APPROX = 28 * DAY
_YEAR_APPROX = 365 * DAY

class _MicroDateTime:
    """
    Internal replacement for datetime object.
    Wraps a Unix timestamp and provides necessary attributes/methods
    by converting to a time tuple when needed.
    """
    __slots__ = '_ts', '_lt' # _ts = timestamp, _lt = localtime tuple

    def __init__(self, timestamp):
        self._ts = int(timestamp)
        self._lt = None # Lazy load localtime tuple

    def _ensure_lt(self):
        # Lazily calculate localtime tuple only when an attribute is accessed
        if self._lt is None:
            self._lt = time.localtime(self._ts)

    @property
    def second(self): self._ensure_lt(); return self._lt[5]
    @property
    def minute(self): self._ensure_lt(); return self._lt[4]
    @property
    def hour(self): self._ensure_lt(); return self._lt[3]
    @property
    def day(self): self._ensure_lt(); return self._lt[2]
    @property
    def month(self): self._ensure_lt(); return self._lt[1] # 1-12
    @property
    def year(self): self._ensure_lt(); return self._lt[0]

    def isoweekday(self):
        """Returns isoweekday (Mon=1, ..., Sun=7)"""
        self._ensure_lt()
        # time.localtime() weekday is Mon=0..Sun=6
        return self._lt[6] + 1

    def replace(self, second=None, minute=None, hour=None, day=None, month=None, year=None, microsecond=None):
        # microsecond is ignored but present in original
        self._ensure_lt()
        lt = list(self._lt)
        # lt tuple: (year, mon, mday, hour, min, sec, wday, yday)
        if year   is not None: lt[0] = year
        if month  is not None: lt[1] = month
        if day    is not None: lt[2] = day
        if hour   is not None: lt[3] = hour
        if minute is not None: lt[4] = minute
        if second is not None: lt[5] = second
        # Note: wday (lt[6]) and yday (lt[7]) are part of the tuple.
        # time.mktime() expects a tuple of at least 8 elements.
        new_ts = time.mktime(tuple(lt))
        return _MicroDateTime(new_ts)

    def __add__(self, other):
        # This implementation assumes 'other' is an integer (seconds)
        if not isinstance(other, (int, float)): raise TypeError("unsupported type")
        return _MicroDateTime(self._ts + int(other))

    def __sub__(self, other):
        if isinstance(other, _MicroDateTime):
            return self._ts - other._ts # Return seconds (int)
        if not isinstance(other, (int, float)): raise TypeError("unsupported type")
        return _MicroDateTime(self._ts - int(other))

    def __lt__(self, other): return self._ts < other._ts
    def __le__(self, other): return self._ts <= other._ts
    def __gt__(self, other): return self._ts > other._ts
    def __ge__(self, other): return self._ts >= other._ts
    def __eq__(self, other): return self._ts == other._ts
    def __ne__(self, other): return self._ts != other._ts
    
    def __repr__(self):
        # Provides a human-readable representation for debugging
        self._ensure_lt()
        return "({:04d}-{:02d}-{:02d} {:02d}:{:02d}:{:02d})".format(
            self._lt[0], self._lt[1], self._lt[2],
            self._lt[3], self._lt[4], self._lt[5])

# --- End of MicroPython datetime replacements ---


_ranges = [
    (0, 59),
    (0, 59),
    (0, 23),
    (1, 31),
    (1, 12),
    (0, 6),
    (1970, 2099),
]

ENTRIES = len(_ranges)
SECOND_OFFSET, MINUTE_OFFSET, HOUR_OFFSET, DAY_OFFSET, MONTH_OFFSET, WEEK_OFFSET, YEAR_OFFSET = range(ENTRIES)

_attribute = [
    'second',
    'minute',
    'hour',
    'day',
    'month',
    'isoweekday',
    'year'
]
_alternate = {
    MONTH_OFFSET: {'jan': 1, 'feb': 2, 'mar': 3, 'apr': 4, 'may': 5, 'jun': 6,
        'jul': 7, 'aug': 8, 'sep': 9, 'oct': 10, 'nov':11, 'dec':12},
    WEEK_OFFSET: {'sun': 0, 'mon': 1, 'tue': 2, 'wed': 3, 'thu': 4, 'fri': 5,
        'sat': 6},
}
_aliases = {
    '@yearly':   '0 0 1 1 *',
    '@annually': '0 0 1 1 *',
    '@monthly':  '0 0 1 * *',
    '@weekly':   '0 0 * * 0',
    '@daily':    '0 0 * * *',
    '@hourly':   '0 * * * *',
}

# Removed WARNING_CHANGE_MESSAGE
# Removed sys.version_info check
_number_types = (int, float)
xrange = range # for Python 3 compat
# Removed WARN_CHANGE

# find the next scheduled time
def _end_of_month(dt): # dt is _MicroDateTime
    ndt = dt + DAY
    while dt.month == ndt.month:
        ndt += DAY
    return ndt.replace(day=1) - DAY # returns _MicroDateTime

def _month_incr(dt, m): # dt is _MicroDateTime
    odt = dt
    dt += _MONTH_APPROX # Use approximation
    while dt.month == odt.month:
        dt += DAY
    # get to the first of next month, let the backtracking handle it
    dt = dt.replace(day=1)
    return dt - odt # Returns int (seconds)

def _year_incr(dt, m): # dt is _MicroDateTime
    # simple leapyear stuff works for 1970-2099 :)
    mod = dt.year % 4
    leap_day_secs = 0
    if mod == 0 and (dt.month, dt.day) < (2, 29):
        leap_day_secs = DAY
    if mod == 3 and (dt.month, dt.day) > (2, 29):
        leap_day_secs = DAY
    return _YEAR_APPROX + leap_day_secs # Return int (seconds)

_increments = [
    lambda *a: SECOND,
    lambda *a: MINUTE,
    lambda *a: HOUR,
    lambda *a: DAY,
    _month_incr,
    lambda *a: DAY,
    _year_incr,
    lambda dt,x: dt.replace(second=0),
    lambda dt,x: dt.replace(minute=0),
    lambda dt,x: dt.replace(hour=0),
    lambda dt,x: dt.replace(day=1) if x > DAY else dt,
    lambda dt,x: dt.replace(month=1) if x > DAY else dt,
    lambda dt,x: dt,
]

# find the previously scheduled time
def _day_decr(dt, m): # dt is _MicroDateTime
    if m.day.input != 'l':
        return -DAY
    odt = dt
    ndt = dt = dt - DAY
    while dt.month == ndt.month:
        dt -= DAY
    return dt - odt # Returns int (seconds)

def _month_decr(dt, m): # dt is _MicroDateTime
    odt = dt
    # get to the last day of last month, let the backtracking handle it
    dt = dt.replace(day=1) - DAY
    return dt - odt # Returns int (seconds)

def _year_decr(dt, m): # dt is _MicroDateTime
    # simple leapyear stuff works for 1970-2099 :)
    mod = dt.year % 4
    leap_day_secs = 0
    if mod == 0 and (dt.month, dt.day) > (2, 29):
        leap_day_secs = DAY
    if mod == 1 and (dt.month, dt.day) < (2, 29):
        leap_day_secs = DAY
    return -(_YEAR_APPROX + leap_day_secs) # Return int (seconds)

def _day_decr_reset(dt, x): # dt is _MicroDateTime
    if x >= -DAY:
        return dt
    cur = dt.month
    while dt.month == cur:
        dt += DAY
    return dt - DAY

_decrements = [
    lambda *a: -SECOND,
    lambda *a: -MINUTE,
    lambda *a: -HOUR,
    _day_decr,
    _month_decr,
    lambda *a: -DAY,
    _year_decr,
    lambda dt,x: dt.replace(second=59),
    lambda dt,x: dt.replace(minute=59),
    lambda dt,x: dt.replace(hour=23),
    _day_decr_reset,
    lambda dt,x: dt.replace(month=12) if x < -DAY else dt,
    lambda dt,x: dt,
    _year_decr,
]

Matcher = namedtuple('Matcher', 'second, minute, hour, day, month, weekday, year')

def _assert(condition, message, *args):
    if not condition:
        if args:
            message = message % args
        raise ValueError(message)

class _Matcher(object):
    __slots__ = 'allowed', 'end', 'any', 'input', 'which', 'split', 'loop'
    def __init__(self, which, entry, loop=False):
        """
        input:
            `which` - index into the increment / validation lookup tables
            `entry` - the value of the column
            `loop` - do we loop when we validate / construct counts
                     (turning 55-5,1 -> 0,1,2,3,4,5,55,56,57,58,59 in a "minutes" column)
        """
        _assert(0 <= which <= YEAR_OFFSET,
            "improper number of cron entries specified")
        self.input = entry.lower()
        self.split = self.input.split(',')
        self.which = which
        self.allowed = set()
        self.end = None
        self.any = '*' in self.split or '?' in self.split
        self.loop = loop

        for it in self.split:
            al, en = self._parse_crontab(which, it)
            if al is not None:
                self.allowed.update(al)
            self.end = en
        _assert(self.end is not None,
            "improper item specification: %r", entry.lower()
        )
        self.allowed = frozenset(self.allowed)

    def __call__(self, v, dt): # dt is _MicroDateTime
        for i, x in enumerate(self.split):
            if x == 'l':
                if v == _end_of_month(dt).day:
                    return True

            elif x.startswith('l'):
                # We have to do this in here, otherwise we can end up, for
                # example, accepting *any* Friday instead of the *last* Friday.
                if dt.month == (dt + WEEK).month: # This now works with _MicroDateTime
                    continue

                x = x[1:]
                if x.isdigit():
                    x = int(x, 10) if x != '7' else 0
                    if v == x:
                        return True
                    continue

                start, end = (int(i, 10) for i in x.partition('-')[::2])
                allowed = set(range(start, end+1))
                if 7 in allowed:
                    allowed.add(0)
                if v in allowed:
                    return True

            elif x.startswith('z'):
                x = x[1:]
                eom = _end_of_month(dt).day # This now works
                if x.isdigit():
                    x = int(x, 10)
                    return (eom - x) == v

                start, end = (int(i, 10) for i in x.partition('-')[::2])
                if v in set(eom - i for i in range(start, end+1)):
                    return True

        return self.any or v in self.allowed

    def __lt__(self, other):
        if self.any:
            return self.end < other
        return all(item < other for item in self.allowed)

    def __gt__(self, other):
        if self.any:
            return _ranges[self.which][0] > other
        return all(item > other for item in self.allowed)

    def __eq__(self, other):
        if self.any:
            return hasattr(other, 'any') and other.any
        if not hasattr(other, 'allowed'):
            return False
        return self.allowed == other.allowed

    def __hash__(self):
        return hash((self.any, self.allowed))

    def _parse_crontab(self, which, entry):
        '''
        This parses a single crontab field and returns the data necessary for
        this matcher to accept the proper values.
        '''

        # this handles day of week/month abbreviations
        def _fix(it):
            if which in _alternate and not it.isdigit():
                if it in _alternate[which]:
                    return _alternate[which][it]
            _assert(it.isdigit(),
                "invalid range specifier: %r (%r)", it, entry)
            it = int(it, 10)
            _assert(_start <= it <= _end_limit,
                "item value %r out of range [%r, %r]",
                it, _start, _end_limit)
            return it

        # this handles individual items/ranges
        def _parse_piece(it):
            if '-' in it:
                start, end = map(_fix, it.split('-'))
                # Allow "sat-sun"
                if which in (DAY_OFFSET, WEEK_OFFSET) and end == 0:
                    end = 7
            elif it == '*':
                start = _start
                end = _end
            else:
                start = _fix(it)
                end = _end
                if increment is None:
                    return set([start])

            _assert(_start <= start <= _end_limit,
                "%s range start value %r out of range [%r, %r]",
                _attribute[which], start, _start, _end_limit)
            _assert(_start <= end <= _end_limit,
                "%s range end value %r out of range [%r, %r]",
                _attribute[which], end, _start, _end_limit)
            if not self.loop:
                _assert(start <= end,
                    "%s range start value %r > end value %r",
                    _attribute[which], start, end)

            if increment and not self.loop:
                next_value = start + increment
                _assert(next_value <= _end_limit,
                        "first next value %r is out of range [%r, %r]",
                        next_value, start, _end_limit)

            if start <= end:
                return set(range(start, end+1, increment or 1))

            # Original logic for looping range (e.g., 55-5 minutes)
            # This is kept from the original library
            right = set(range(_start, end + 1, increment or 1))
            left = set(range(start, _end + 1, increment or 1))
            return left | right


        _start, _end = _ranges[which]
        _end_limit = _end
        # wildcards
        if entry in ('*', '?'):
            if entry == '?':
                _assert(which in (DAY_OFFSET, WEEK_OFFSET),
                    "cannot use '?' in the %r field", _attribute[which])
            return None, _end

        # last day of the month
        if entry == 'l':
            _assert(which == DAY_OFFSET,
                "you can only specify a bare 'L' in the 'day' field")
            return None, _end

        # for the days before the last day of the month
        elif entry.startswith('z'):
            _assert(which == DAY_OFFSET,
                "you can only specify a leading 'Z' in the 'day' field")
            es, _, ee = entry[1:].partition('-')
            _assert((entry[1:].isdigit() and 0 <= int(es, 10) <= 7) or
                    (_ and es.isdigit() and ee.isdigit() and 0 <= int(es, 10) <= 7 and 1 <= int(ee, 10) <= 7 and es <= ee),
                "<day> specifier must include a day number or range 0..7 in the 'day' field, you entered %r", entry)
            return None, _end

        # for the last 'friday' of the month, for example
        elif entry.startswith('l'):
            _assert(which == WEEK_OFFSET,
                "you can only specify a leading 'L' in the 'weekday' field")
            es, _, ee = entry[1:].partition('-')
            _assert((entry[1:].isdigit() and 0 <= int(es, 10) <= 7) or
                    (_ and es.isdigit() and ee.isdigit() and 0 <= int(es, 10) <= 7 and 0 <= int(ee, 10) <= 7),
                "last <day> specifier must include a day number or range 0..7 in the 'weekday' field, you entered %r", entry)
            return None, _end

        # allow Sunday to be specified as weekday 7
        if which == WEEK_OFFSET:
            _end_limit = 7

        increment = None
        # increments
        if '/' in entry:
            entry, increment = entry.split('/')
            increment = int(increment, 10)
            _assert(increment > 0,
                "you can only use positive increment values, you provided %r",
                increment)
            _assert(increment <= _end_limit,
                    "increment value must be less than %r, you provided %r",
                    _end_limit, increment)

        # handle singles and ranges
        good = _parse_piece(entry)

        # change Sunday to weekday 0
        if which == WEEK_OFFSET and 7 in good:
            good.discard(7)
            good.add(0)

        return good, _end

# --- MODIFICATION: Use _pm_instance for _gv ---
def _get_random_second():
    ts = 0
    if _pm_instance:
        try:
            ts = _pm_instance.get_unix_time()
        except Exception:
            pass # Will use fallback
    
    if not ts: # Fallback if pm fails or doesn't exist
        try:
            ts = int(time.time())
        except Exception:
            ts = 0 # Final fallback
            
    return str(int(ts) % 60)

_gv = _get_random_second
# --- END OF MODIFICATION ---


class CronTab(object):
    __slots__ = 'matchers', 'rs'
    def __init__(self, crontab, loop=False, random_seconds=False):
        self.rs = random_seconds
        self.matchers = self._make_matchers(crontab, loop, random_seconds)

    def __eq__(self, other):
        if not isinstance(other, CronTab):
            return False
        # Compare matchers (which are _Matcher objects)
        # Need to compare them field by field as 'matchers' is a namedtuple
        match_last = (self.matchers.minute == other.matchers.minute and
                      self.matchers.hour == other.matchers.hour and
                      self.matchers.day == other.matchers.day and
                      self.matchers.month == other.matchers.month and
                      self.matchers.weekday == other.matchers.weekday and
                      self.matchers.year == other.matchers.year)
        
        return match_last and ((self.rs and other.rs) or (not self.rs and
            not other.rs and self.matchers.second == other.matchers.second))

    def _make_matchers(self, crontab, loop, random_seconds):
        '''
        This constructs the full matcher struct.
        '''
        crontab = _aliases.get(crontab, crontab)
        ct = crontab.split()

        if len(ct) == 5:
            ct.insert(0, _gv() if random_seconds else '0')
            ct.append('*')
        elif len(ct) == 6:
            ct.insert(0, _gv() if random_seconds else '0')
        _assert(len(ct) == 7,
            "improper number of cron entries specified; got %i need 5 to 7"%(len(ct,)))

        matchers = [_Matcher(which, entry, loop) for which, entry in enumerate(ct)]

        return Matcher(*matchers)

    def _test_match(self, index, dt): # dt is _MicroDateTime
        '''
        This tests the given field for whether it matches with the current
        _MicroDateTime object passed.
        '''
        at = _attribute[index] # e.g., 'isoweekday'
        
        if at == 'isoweekday':
            attr = dt.isoweekday() # Call method
        else:
            attr = getattr(dt, at) # Get property
        
        if index == WEEK_OFFSET:
            attr = attr % 7 # isoweekday() % 7 -> Mon=1..Sat=6, Sun=0
            # This matches the _alternate table logic (sun=0, mon=1)
        
        return self.matchers[index](attr, dt)

    # --- MODIFICATION: Use _pm_instance for current time ---
    def _default_now(self):
        # Adapted to use the global PowerManager instance if it exists
        if _pm_instance:
            try:
                return _pm_instance.get_unix_time()
            except Exception as e:
                utils.log_error("Error in crontab _default_now (pm):", e)
                # Attempt fallback
        
        # Fallback if _pm_instance doesn't exist or failed
        try:
            return int(time.time())
        except: # Final fallback
            utils.log_error("Error in crontab _default_now (time.time), using 0.")
            return 0
    # --- END OF MODIFICATION ---

    def next(self, now=None, increments=_increments, delta=True, default_utc=False, return_datetime=False):
        '''
        How long to wait in seconds before this crontab entry can next be
        executed.
        'now' should be a Unix timestamp (integer).
        '''
        # Removed all 'warnings' and 'WARN_CHANGE' logic
        # default_utc is ignored, as MicroPython time functions are UTC-based
        
        if now is None:
            now = self._default_now() # Get timestamp
        
        if not isinstance(now, _MicroDateTime):
            # Assume it's a timestamp (int)
            now = _MicroDateTime(int(now))

        # Removed timezone logic
        onow, now = now, now
        
        # Start 1 second in the future
        future = now + increments[0]() # + 1 second
        
        if future < now:
            # we are going backwards...
            _test = lambda: future.year < self.matchers.year
        else:
            # we are going forwards
            _test = lambda: self.matchers.year < future.year

        to_test = ENTRIES - 1
        while to_test >= 0:
            if not self._test_match(to_test, future):
                inc = increments[to_test](future, self.matchers) # inc is int (seconds)
                future = future + inc
                for i in xrange(0, to_test):
                    future = increments[ENTRIES+i](future, inc)
                try:
                    if _test():
                        return None # Reached end of time
                except Exception as e:
                    utils.log_error(future, type(future), type(inc))
                    raise
                to_test = ENTRIES-1
                continue
            to_test -= 1

        # verify the match
        match = [self._test_match(i, future) for i in xrange(ENTRIES)]
        _assert(all(match),
                "\nYou have discovered a bug with crontab, please notify the\n" \
                "author with the following information:\n" \
                "crontab: %r\n" \
                "now: %r", ' '.join(m.input for m in self.matchers), now)

        if return_datetime:
            return future # Return _MicroDateTime object

        if not delta:
            now = _MicroDateTime(0) # 1970-01-01

        delay = future - now # Returns int (seconds)
        
        # Removed timezone logic
        
        return float(delay) # Return seconds as float

    def previous(self, now=None, delta=True, default_utc=False, return_datetime=False):
        # Removed WARN_CHANGE
        return self.next(now, _decrements, delta, default_utc, return_datetime)

    def test(self, now = None):
        if now is None:
            now = self._default_now() # Get timestamp
        
        if not isinstance(now, _MicroDateTime):
            # Assume it's a timestamp (int)
            now = _MicroDateTime(int(now))

        # Removed timezone logic
        onow, now = now, now
        if isinstance(now, _number_types):
            now = _MicroDateTime(int(now))
        # Assume 'entry' is a _MicroDateTime object
        for index in xrange(ENTRIES):
            if not self._test_match(index, now):
                return False
        return True