
from degreedays._private import XmlElement
import degreedays._private as private
import degreedays.time
import degreedays.geo
import degreedays.api.data as data
import re

# Define __all__ as it's the easiest way to make sure that none of our other
# imports (things from geo, time, and _private) become available to anyone that
# does an import * on this module.
__all__ = ['StationIdLocation', 'LongLatLocation', 'PostalCodeLocation',
    'LatestValuesPeriod', 'DayRangePeriod',
    'DailyBreakdown', 'MonthlyBreakdown', 'YearlyBreakdown',
    'FullYearsAverageBreakdown',
    'HeatingDegreeDaysCalculation', 'CoolingDegreeDaysCalculation']

class StationIdLocation(data.Location):
    __slots__ = ('__stationId',)
    def __init__(self, stationId):
        self.__stationId = private.checkStationId(stationId, True).upper()
    def _equalityFields(self):
        return (self.__stationId,)
    @property
    def stationId(self): return self.__stationId
    def __repr__(self):
        return "StationIdLocation('%s')" % self.__stationId
    def _toXml(self):
        return XmlElement("StationIdLocation").addChild(
                XmlElement("StationId").setValue(self.__stationId))  

class LongLatLocation(data.GeographicLocation):
    __slots__ = ('__longLat',)
    def __init__(self, longLat):
        self.__longLat = degreedays.geo.LongLat._check(longLat)
    def _equalityFields(self):
        return (self.__longLat,)
    @property
    def longLat(self): return self.__longLat
    def __repr__(self):
        return 'LongLatLocation(%r)' % self.__longLat
    def _toXml(self):
        return XmlElement("LongLatLocation").addChild(
                self.__longLat._toXml())     

# See notes in private on regexp testing.
_POSTAL_CODE_REGEXP_STRING = '[- 0-9a-zA-Z]{1,16}$' 
_POSTAL_CODE_REGEXP = re.compile(_POSTAL_CODE_REGEXP_STRING)
def _getValidPostalCode(postalCode):
    private.checkString(postalCode, 'postalCode')
    # Work on assumption that this could be user input, so auto-correct for
    # leading or trailing whitespace.
    postalCode = postalCode.strip()
    if not _POSTAL_CODE_REGEXP.match(postalCode):
        raise ValueError('Invalid postalCode (%r) - it should match the '
            'regular expression %s.' % (postalCode, _POSTAL_CODE_REGEXP_STRING))
    return postalCode.upper()

_COUNTRY_CODE_REGEXP = re.compile('[A-Z]{2}$')   
def _getValidCountryCode(countryCode):
    private.checkString(countryCode, 'countryCode')
    # Be strict about this - it's unlikely to be user input as the user would
    # probably select from a list of countries mapped to valid codes.  i.e. we
    # don't do any whitespace stripping, and we're strict about case.
    if not _COUNTRY_CODE_REGEXP.match(countryCode):
        raise ValueError('Invalid country code (%r) - it should be 2 upper-'
            'case alphabetical characters (A - Z).' % countryCode)
    return countryCode
    
class PostalCodeLocation(data.GeographicLocation):
    __slots__ = ('__postalCode', '__countryCode')
    def __init__(self, postalCode, countryCode):
        self.__postalCode = _getValidPostalCode(postalCode)
        self.__countryCode = _getValidCountryCode(countryCode)
    def _equalityFields(self):
        return (self.__postalCode, self.__countryCode)
    @property
    def postalCode(self): return self.__postalCode
    @property
    def countryCode(self): return self.__countryCode
    def __repr__(self):
        return ("PostalCodeLocation('%s', '%s')" %
            (self.__postalCode, self.__countryCode))
    def _toXml(self):
        e = XmlElement("PostalCodeLocation")
        e.addChild(XmlElement("PostalCode").setValue(self.__postalCode))
        e.addChild(XmlElement("CountryCode").setValue(self.__countryCode))
        return e
                
class LatestValuesPeriod(data.Period):
    __slots__ = ('__numberOfValues', '__minimumNumberOfValuesOrNone')
    def __init__(self, numberOfValues, minimumNumberOfValuesOrNone = None):
        self.__numberOfValues = private.checkInt(
            numberOfValues, 'numberOfValues')
        if numberOfValues < 1:
            raise ValueError('Invalid numberOfValues (%s) - cannot be < 1.'
                % numberOfValues)
        self.__minimumNumberOfValuesOrNone = minimumNumberOfValuesOrNone
        if minimumNumberOfValuesOrNone is not None:
            private.checkInt(minimumNumberOfValuesOrNone, 'minimumNumberOfValuesOrNone')
            if minimumNumberOfValuesOrNone < 1:
                raise ValueError('Invalid minimumNumberOfValuesOrNone (%s) - cannot '
                    'be < 1 (though it can be None if there is to be no '
                    'minimum (the default).' % minimumNumberOfValuesOrNone)
            elif minimumNumberOfValuesOrNone > numberOfValues:
                raise ValueError('Invalid minimumNumberOfValuesOrNone (%s) - cannot '
                    'be > numberOfValues (%s).' %
                    (minimumNumberOfValuesOrNone, numberOfValues))
    def _equalityFields(self):
        return (self.__numberOfValues, self.__minimumNumberOfValuesOrNone)
    @property
    def numberOfValues(self): return self.__numberOfValues
    @property
    def minimumNumberOfValuesOrNone(self): return self.__minimumNumberOfValuesOrNone
    def __repr__(self):
        if self.__minimumNumberOfValuesOrNone is None:
            return 'LatestValuesPeriod(%d)' % self.__numberOfValues
        else:
            return 'LatestValuesPeriod(%d, %d)' % \
                (self.__numberOfValues, self.__minimumNumberOfValuesOrNone)   
    def _toXml(self):
        e = XmlElement("LatestValuesPeriod").addChild(
            XmlElement("NumberOfValues").setValue(self.__numberOfValues))
        if (self.__minimumNumberOfValuesOrNone is not None):
            e.addChild(XmlElement("MinimumNumberOfValues").setValue(
                self.__minimumNumberOfValuesOrNone))
        return e
        
class DayRangePeriod(data.Period):
    __slots__ = ('__dayRange', '__minimumDayRangeOrNone')
    def __init__(self, dayRange, minimumDayRangeOrNone = None):
        self.__dayRange = degreedays.time.DayRange._check(dayRange)
        if minimumDayRangeOrNone is not None:
            degreedays.time.DayRange._check(minimumDayRangeOrNone)
        self.__minimumDayRangeOrNone = minimumDayRangeOrNone
    def _equalityFields(self):
        return (self.__dayRange, self.__minimumDayRangeOrNone)
    @property
    def dayRange(self): return self.__dayRange
    @property
    def minimumDayRangeOrNone(self): return self.__minimumDayRangeOrNone
    def __repr__(self):
        if self.__minimumDayRangeOrNone is None:
            return 'DayRangePeriod(%r)' % self.__dayRange
        else:
            return 'DayRangePeriod(%r, %r)' % \
                (self.__dayRange, self.__minimumDayRangeOrNone)
    def _toXml(self):
        e = XmlElement("DayRangePeriod").addChild(self.__dayRange._toXml())
        if (self.__minimumDayRangeOrNone is not None):
            e.addChild(self.__minimumDayRangeOrNone._toXml('MinimumDayRange'))
        return e;

class DailyBreakdown(data.DatedBreakdown):
    __slots__ = ('__period')
    def __init__(self, period):
        self.__period = data.Period._check(period)
    def _equalityFields(self):
        return (self.__period,)
    @property
    def period(self): return self.__period
    def __repr__(self):
        return 'DailyBreakdown(%r)' % self.__period
    def _toXml(self):
        return XmlElement("DailyBreakdown").addChild(self.__period._toXml())
    
class WeeklyBreakdown(data.DatedBreakdown):
    __slots__ = ('__period', '__firstDayOfWeek')
    def __init__(self, period, firstDayOfWeek):
        self.__period = data.Period._check(period)
        self.__firstDayOfWeek = degreedays.time.DayOfWeek._check(
            firstDayOfWeek, 'firstDayOfWeek')
    def _equalityFields(self):
        return (self.__period, self.__firstDayOfWeek)
    @property
    def period(self): return self.__period
    @property
    def firstDayOfWeek(self): return self.__firstDayOfWeek
    def __repr__(self):
        return ('WeeklyBreakdown(%r, %r)' %
            (self.__period, self.__firstDayOfWeek))
    def _toXml(self):
        e = XmlElement('WeeklyBreakdown') \
            .addChild(self.__period._toXml())
        e.addAttribute('firstDayOfWeek', str(self.__firstDayOfWeek))
        return e
        
class MonthlyBreakdown(data.DatedBreakdown):
    __slots__ = ('__period', '__startOfMonth')
    def __init__(self, period, startOfMonth=degreedays.time.StartOfMonth(1)):
        self.__period = data.Period._check(period)
        self.__startOfMonth = degreedays.time.StartOfMonth._check(startOfMonth)
    def _equalityFields(self):
        return (self.__period, self.__startOfMonth)
    @property
    def period(self): return self.__period
    @property
    def startOfMonth(self): return self.__startOfMonth
    def __repr__(self):
        if self.__startOfMonth.dayOfMonth == 1:
            return 'MonthlyBreakdown(%r)' % self.__period
        else:
            return ('MonthlyBreakdown(%r, %r)' % 
                (self.__period, self.__startOfMonth))
    def _toXml(self):
        e = XmlElement('MonthlyBreakdown') \
            .addChild(self.__period._toXml())
        if (self.__startOfMonth.dayOfMonth != 1):
            e.addAttribute('startOfMonth', str(self.__startOfMonth))
        return e;
        
class YearlyBreakdown(data.DatedBreakdown):
    __slots__ = ('__period', '__startOfYear')
    def __init__(self, period, startOfYear=degreedays.time.StartOfYear(1, 1)):
        self.__period = data.Period._check(period)
        self.__startOfYear = degreedays.time.StartOfYear._check(startOfYear)
    def _equalityFields(self):
        return (self.__period, self.__startOfYear)
    @property
    def period(self): return self.__period
    @property
    def startOfYear(self): return self.__startOfYear
    def __repr__(self):
        if self.__startOfYear == degreedays.time.StartOfYear(1, 1):
            return 'YearlyBreakdown(%r)' % self.__period
        else:
            return ('YearlyBreakdown(%r, %r)' %
                (self.__period, self.__startOfYear))
    def _toXml(self):
        e = XmlElement('YearlyBreakdown').addChild(self.period._toXml())
        if (self.startOfYear != degreedays.time.StartOfYear(1, 1)):
            e.addAttribute('startOfYear', str(self.startOfYear))
        return e;
    
class FullYearsAverageBreakdown(data.AverageBreakdown):
    __slots__ = ('__period',)
    def __init__(self, period):
        self.__period = data.Period._check(period)
    def _equalityFields(self):
        return (self.__period,)
    @property
    def period(self): return self.__period
    def __repr__(self):
        return 'FullYearsAverageBreakdown(%r)' % self.__period
    def _toXml(self):
        return (XmlElement('FullYearsAverageBreakdown')
            .addChild(self.period._toXml()))
            
class HeatingDegreeDaysCalculation(data.Calculation):
    __slots__ = ('__baseTemperature',)
    def __init__(self, baseTemperature):
        self.__baseTemperature = data.Temperature._check(
            baseTemperature, 'baseTemperature')
    def _equalityFields(self):
        return (self.__baseTemperature,)
    @property
    def baseTemperature(self): return self.__baseTemperature
    def __repr__(self):
        return 'HeatingDegreeDaysCalculation(%r)' % self.__baseTemperature
    def _toXml(self):
        return XmlElement('HeatingDegreeDaysCalculation').addChild(
                self.__baseTemperature._toXml('BaseTemperature'))

class CoolingDegreeDaysCalculation(data.Calculation):
    __slots__ = ('__baseTemperature',)
    def __init__(self, baseTemperature):
        self.__baseTemperature = data.Temperature._check(
            baseTemperature, 'baseTemperature')
    def _equalityFields(self):
        return (self.__baseTemperature,)
    @property
    def baseTemperature(self): return self.__baseTemperature
    def __repr__(self):
        return 'CoolingDegreeDaysCalculation(%r)' % self.__baseTemperature
    def _toXml(self):
        return XmlElement('CoolingDegreeDaysCalculation').addChild(
                self.__baseTemperature._toXml('BaseTemperature'))
    