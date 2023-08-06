
from degreedays._private import Immutable, XmlElement
import degreedays._private as private

__all__ = ['LongLat', 'DistanceUnit', 'Distance']

# Allows for slight rounding errors on calculated longitude and latitude values.
_MARGIN = 0.001
class LongLat(Immutable):
    __slots__ = ('__longitude', '__latitude')
    def __fail(self, longitude, latitude):
        raise ValueError("Problem longitude (%r) or latitude (%r)." %
                         (longitude, latitude));
    def __init__(self, longitude, latitude):
        longitude = private.checkNumeric(longitude, 'longitude')
        latitude = private.checkNumeric(latitude, 'latitude')
        if longitude > 180.0:
            if longitude > 180.0 + _MARGIN:
                self.__fail(longitude, latitude)
            longitude = 180.0
        elif longitude < -180.0:
            if longitude < -180.0 - _MARGIN:
                self.__fail(longitude, latitude)
        if latitude > 90.0:
            if latitude > 90.0 + _MARGIN:
                self.__fail(longitude, latitude)
            latitude = 90.0
        elif latitude < -90.0:
            if latitude < -90.0 - _MARGIN:
                self.__fail(longitude, latitude)
            latitude = -90.0
        self.__longitude = longitude
        self.__latitude = latitude
    def _equalityFields(self):
        return (self.__longitude, self.__latitude)
    @property
    def longitude(self): return self.__longitude
    @property
    def latitude(self): return self.__latitude
    def __repr__(self):
        return 'LongLat(%f, %f)' % (self.__longitude, self.__latitude)
    def _toXml(self):
        # Will str localize it?  Hard to find in docs, but I tested it with
        # Windows set to a french locale and it didn't, which is good.
        return (XmlElement("LongLat")
                .addAttribute("longitude", str(self.__longitude))
                .addAttribute("latitude", str(self.__latitude)))
    @classmethod
    def _check(cls, param, paramName='longLat'):
        if not isinstance(param, LongLat):
            raise TypeError(private.wrongTypeString(param, paramName, LongLat,
                'LongLat(-74.0064, 40.7142)'))
        return param

# See TemperatureUnit for an explanation of this pattern
class _DistanceUnitMetaclass(type):
    def __iter__(self):
        for u in (DistanceUnit.METRES, DistanceUnit.KILOMETRES,
                DistanceUnit.FEET, DistanceUnit.MILES):
            yield u
_DistanceUnitSuper = _DistanceUnitMetaclass('_DistanceUnitSuper', (Immutable,),
    {'__slots__': ()})
_FEET_IN_METRE = 3.28083989501 
class DistanceUnit(_DistanceUnitSuper):
    __slots__ = ('__symbol', '__singularName', '__pluralName', '__isMetric',
        '__noOfBase', '__pluralNameUpper')
    __map = {}
    # Below are set later.  We want them defined here as class variables so that
    # they show up in intellisense if you type "DayOfWeek.".
    METRES = None
    KILOMETRES = None
    FEET = None
    MILES = None
    def __initImpl(self, singularName, pluralName, isMetric, noOfBase):
        self.__singularName = singularName
        self.__pluralName = pluralName
        self.__isMetric = isMetric
        self.__noOfBase = noOfBase
        self.__pluralNameUpper = pluralName.upper()
    def __init__(self, symbol):
        if symbol == 'm' and DistanceUnit.METRES is None:
            self.__initImpl('metre', 'metres', True, 1)
        elif symbol == 'km' and DistanceUnit.KILOMETRES is None:
            self.__initImpl('kilometre', 'kilometres', True, 1000)
        elif symbol == 'ft' and DistanceUnit.FEET is None:
            self.__initImpl('foot', 'feet', False, 1)
        elif symbol == 'mi' and DistanceUnit.MILES is None:
            self.__initImpl('mile', 'miles', False, 5280)
        else:
            raise TypeError('This is not built for direct '
                'instantiation.  Please use DistanceUnit.METRES, '
                'DistanceUnit.KILOMETRES, DistanceUnit.FEET, or '
                'DistanceUnit.MILES.')
        self.__symbol = symbol
        DistanceUnit.__map[symbol] = self
    def _equalityFields(self):
        return (self.__symbol,)
    def __convertValueToSameSchemeUnit(self, value, sameSchemeUnit):
        if self == sameSchemeUnit:
            return value
        elif sameSchemeUnit.__noOfBase == 1:
            return value * self.noOfBase
        elif self.__noOfBase == 1:
            return value / sameSchemeUnit.noOfBase
        else:
            raise ValueError('This should not happen with the range of units '
                'we have')
    def _convertValue(self, value, newUnit):
        if self.__isMetric == newUnit.__isMetric:
            return self.__convertValueToSameSchemeUnit(value, newUnit)
        elif self.__isMetric:
            inMetres = self.__convertValueToSameSchemeUnit(
                value, DistanceUnit.METRES)
            inFeet = inMetres * _FEET_IN_METRE
            return DistanceUnit.FEET.__convertValueToSameSchemeUnit(
                inFeet, newUnit)
        else:
            inFeet = self.__convertValueToSameSchemeUnit(
                value, DistanceUnit.FEET)
            inMetres = inFeet / _FEET_IN_METRE
            return DistanceUnit.METRES.__convertValueToSameSchemeUnit(
                inMetres, newUnit)
    def __str__(self):
        return self.__pluralName
    def __repr__(self):
        return 'DistanceUnit.' + self.__pluralNameUpper
    @property # as property to make it immutable (or as much as is possible)
    def _symbol(self): return self.__symbol
    @classmethod
    def _check(cls, param, paramName='distanceUnit'):
        if not isinstance(param, DistanceUnit):
            raise TypeError(private.wrongTypeString(param, paramName,
                DistanceUnit, 'DistanceUnit.METRES, DistanceUnit.KILOMETRES, '
                'DistanceUnit.FEET, DistanceUnit.MILES'))
        return param
DistanceUnit.METRES = DistanceUnit('m')
DistanceUnit.KILOMETRES = DistanceUnit('km')
DistanceUnit.FEET = DistanceUnit('ft')
DistanceUnit.MILES = DistanceUnit('mi')

class Distance(Immutable):
    __slots__ = ('__value', '__unit')
    def __init__(self, value, unit):
        self.__value = private.checkNumeric(value, 'value')
        self.__unit = DistanceUnit._check(unit, 'unit')
    def _equalityFields(self):
        return (self.__value, self.__unit)
    @property
    def value(self): return self.__value
    @property
    def unit(self): return self.__unit
    @classmethod
    def metres(cls, value):
        return Distance(value, DistanceUnit.METRES)
    @classmethod
    def kilometres(cls, value):
        return Distance(value, DistanceUnit.KILOMETRES)
    @classmethod
    def feet(cls, value):
        return Distance(value, DistanceUnit.FEET)
    @classmethod
    def miles(cls, value):
        return Distance(value, DistanceUnit.MILES)
    def __toUnit(self, newUnit):
        if newUnit == self.__unit:
            return self
        return Distance(self.__unit._convertValue(self.__value, newUnit),
            newUnit)
    def inMetres(self):
        return self.__toUnit(DistanceUnit.METRES)
    def inKilometres(self):
        return self.__toUnit(DistanceUnit.KILOMETRES)
    def inFeet(self):
        return self.__toUnit(DistanceUnit.FEET)
    def inMiles(self):
        return self.__toUnit(DistanceUnit.MILES)
    # "in" is a reserved word so we can't use that.  PEP8 recommends to add a
    # trailing underscore and this seems to be a kind of convention in Python.
    def in_(self, newUnit): 
        return self.__toUnit(newUnit)
    def __str__(self):
        return '%g %s' % (self.__value, self.__unit._symbol)
    def __repr__(self):
        return 'Distance.%s(%g)' % (self.__unit, self.__value)
    @classmethod
    def _check(cls, param, paramName='distance'):
        if not isinstance(param, Distance):
            raise TypeError(private.wrongTypeString(param, paramName, Distance,
                'Distance.metres(20)'))
        return param