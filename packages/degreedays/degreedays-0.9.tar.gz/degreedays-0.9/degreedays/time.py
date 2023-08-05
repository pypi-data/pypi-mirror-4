
#from datetime import date

from degreedays._private import Immutable
from degreedays._private import XmlElement
import degreedays._private as private

__all__ = ['DayRange', 'DayOfWeek', 'StartOfMonth', 'StartOfYear']

_DAY_RANGE_EXAMPLE = ('DayRange(datetime.date(2012, 1, 1), '
        'datetime.date(2012, 11, 30)) '
    'or DayRange.singleDay(datetime.date.today() - datetime.timedelta(1)) '
    '(for yesterday only)')
# using datetime.date is perfect for us as it's timezone independent.
class DayRange(Immutable):
    __slots__ = ('__first', '__last')
    def __init__(self, first, last):
        if (first > last):
            raise ValueError("first (%r) cannot be > last (%r)" % (first, last))
        self.__first = first
        self.__last = last
    def _equalityFields(self):
        return (self.__first, self.__last)
    @classmethod
    def singleDay(cls, firstAndLast):
        return DayRange(firstAndLast, firstAndLast)
    @property
    def first(self): return self.__first
    @property
    def last(self): return self.__last
    def __len__(self):
        return (self.last - self.first).days
    def __repr__(self):
        return 'DayRange(%r, %r)' % (self.__first, self.__last)
    def _toXml(self, elementName = "DayRange"):
        # NB \ is line-continuation character, as mentioned at:
        # http://stackoverflow.com/questions/8683178/
        return XmlElement(elementName) \
                .addAttribute("first", self.__first.isoformat()) \
                .addAttribute("last", self.__last.isoformat())
    @classmethod
    def _check(cls, param, paramName='dayRange'):
        if not isinstance(param, DayRange):
            raise TypeError(private.wrongSupertypeString(param, paramName,
                DayRange, _DAY_RANGE_EXAMPLE))
        return param

_DAY_OF_WEEK_EXAMPLE = ('DayOfWeek.MONDAY, DayOfWeek.TUESDAY, ..., or '
    'DayOfWeek(0) for Monday etc. (using the int constants that Python uses in '
    'its calendar module)')
# This metaclass stuff is to make it possible to iterate over the values, like
# "for dow in DayOfWeek".  See TemperatureUnit for an explanation and
# references.
class _DayOfWeekMetaclass(type):
    def __iter__(self):
        for i in range(7):
            yield DayOfWeek(i)
_DayOfWeekSuper = _DayOfWeekMetaclass('_DayOfWeekSuper', (Immutable,),
    {'__slots__': ()})            
class DayOfWeek(_DayOfWeekSuper):
    __slots__ = ('__index', '__name', '__nameUpper', '__isoIndex')
    __map = {}
    # Below are set later.  We want them defined here as class variables so that
    # they show up in intellisense if you type "DayOfWeek.".
    MONDAY = None
    TUESDAY = None
    WEDNESDAY = None
    THURSDAY = None
    FRIDAY = None
    SATURDAY = None
    SUNDAY = None
    def __init__(self, index):
        if index == 0:
            self.__name = 'Monday'
        elif index == 1:
            self.__name = 'Tuesday'
        elif index == 2:
            self.__name = 'Wednesday'
        elif index == 3:
            self.__name = 'Thursday'
        elif index == 4:
            self.__name = 'Friday'
        elif index == 5:
            self.__name = 'Saturday'
        elif index == 6:
            self.__name = 'Sunday'
        else:
            raise ValueError('Invalid int value for day of week (%r) - '
                'expecting int between 0 (Monday) and 6 (Sunday).')
        self.__nameUpper = self.__name.upper()
        self.__index = index
        self.__isoIndex = index + 1
    # We need this because of the way we're caching values and allowing direct
    # use of the constructor with indexes e.g. DayOfWeek(0) for Monday.  This
    # prevents direct use of the constructor from creating a new instance each
    # time.
    def __new__(cls, index):
        existing = DayOfWeek.__map.get(index, None)
        if existing is not None:
            return existing
        newItem = super(DayOfWeek, cls).__new__(cls)
        # We don't need to call __init__... python does it for us after this
        # __new__ method has returned the un-initialized item.  And it passes
        # the index parameter to __init__ as well.
        DayOfWeek.__map[index] = newItem
        return newItem
    def _equalityFields(self):
        return (self.__index,)
    @property
    def index(self): return self.__index
    @property
    def isoIndex(self): return self.__isoIndex
    def __str__(self):
        return self.__name
    def __repr__(self):
        return 'DayOfWeek.' + self.__nameUpper
    @classmethod
    def _check(cls, param, paramName='dayOfWeek'):
        if not isinstance(param, DayOfWeek):
            raise TypeError(private.wrongSupertypeString(param, paramName,
                DayOfWeek, _DAY_OF_WEEK_EXAMPLE))
        return param
    
DayOfWeek.MONDAY = DayOfWeek(0)
DayOfWeek.TUESDAY = DayOfWeek(1)
DayOfWeek.WEDNESDAY = DayOfWeek(2)
DayOfWeek.THURSDAY = DayOfWeek(3)
DayOfWeek.FRIDAY = DayOfWeek(4)
DayOfWeek.SATURDAY = DayOfWeek(5)
DayOfWeek.SUNDAY = DayOfWeek(6)              

_START_OF_MONTH_EXAMPLE = ("StartOfMonth(1) for regular calendar months "
    "starting on the 1st of each month, "
    "StartOfMonth(2) for the \"months\" starting on the 2nd of each month, "
    "etc.")
class StartOfMonth(Immutable):
    __slots__ = ('__dayOfMonth',)
    def __init__(self, dayOfMonth):
        private.checkInt(dayOfMonth, 'dayOfMonth')
        if (dayOfMonth < 1 or dayOfMonth > 28):
            raise ValueError('Invalid dayOfMonth (' +
                str(dayOfMonth) + ') - it cannot be less than 1 '
                'or greater than 28 (to ensure it can work for all '
                'months of all years).')
        self.__dayOfMonth = dayOfMonth
    def _equalityFields(self):
        return (self.__dayOfMonth,)
    @property
    def dayOfMonth(self): return self.__dayOfMonth
    def __repr__(self):
        return 'StartOfMonth(%d)' % self.__dayOfMonth
    def __str__(self):
        return '---%02d' % self.__dayOfMonth
    @classmethod
    def _check(cls, param, paramName='startOfMonth'):
        if not isinstance(param, StartOfMonth):
            raise TypeError(private.wrongSupertypeString(param, paramName,
                StartOfMonth, _START_OF_MONTH_EXAMPLE))
        return param
    
def _minNoDaysInMonth(monthOfYear):
    return [
        0, # dummy value, just so the first month index is 1.
        31, # Jan
        29, # Feb
        31, # Mar
        30, # Apr
        31, # May
        30, # Jun
        31, # Jul
        31, # Aug
        30, # Sep
        31, # Oct
        30, # Nov
        31 # Dec
    ][monthOfYear]

_START_OF_YEAR_EXAMPLE = ("StartOfYear(1, 1) for regular calendar years "
    "starting on the 1st of January, "
    "StartOfYear(4, 6) for \"years\" starting on the 6th of April, etc.")
class StartOfYear(Immutable):
    __slots__ = ('__monthOfYear', '__dayOfMonth')
    def __init__(self, monthOfYear, dayOfMonth):
        private.checkInt(monthOfYear, 'monthOfYear')
        private.checkInt(dayOfMonth, 'dayOfMonth')
        if (monthOfYear < 1 or monthOfYear > 12):
            raise ValueError('Invalid monthOfYear (' + str(monthOfYear) +
                ') - it cannot be less than 1 (January) or greater than 12 '
                '(December).')
        if (dayOfMonth < 1):
            raise ValueError('Invalid dayOfMonth (' + str(dayOfMonth) +
                ') - it cannot be less than 1.');
        if (monthOfYear == 2 and dayOfMonth > 28):
            raise ValueError('Invalid dayOfMonth (' + str(dayOfMonth) + ') - '
                'when when the month is February (2), the day cannot be '
                'greater than 28.')
        noDaysInMonth = _minNoDaysInMonth(monthOfYear)
        if (dayOfMonth > noDaysInMonth):
            raise ValueError('Invalid dayOfMonth (' + str(dayOfMonth) +
                ') - it cannot be greater than ' + str(noDaysInMonth) +
                ' when the month is ' + str(monthOfYear) + '.')
        self.__monthOfYear = monthOfYear
        self.__dayOfMonth = dayOfMonth
    def _equalityFields(self):
        return (self.__monthOfYear, self.__dayOfMonth)
    @property
    def monthOfYear(self): return self.__monthOfYear
    @property
    def dayOfMonth(self): return self.__dayOfMonth
    def __repr__(self):
        return 'StartOfYear(%d, %d)' % (self.__monthOfYear, self.__dayOfMonth)
    def __str__(self):
        return '--%02d-%02d' % (self.monthOfYear, self.dayOfMonth)
    @classmethod
    def _check(cls, param, paramName='startOfYear'):
        if not isinstance(param, StartOfYear):
            raise TypeError(private.wrongSupertypeString(param, paramName,
                StartOfYear, _START_OF_YEAR_EXAMPLE))
        return param
