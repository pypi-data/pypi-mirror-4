
import re

# For immutable types we started out using a variation on namedtuple, inspired
# by the code at:
# http://blog.thomnichols.org/2010/12/lightweight-data-types-in-python
# and also the source code for namedtuple:
# http://svn.python.org/view/python/branches/release26-maint/Lib/collections.py?revision=72955&view=markup
# Downside was that namedtuple required Python 2.6+, it wasn't so great for
# documentation (parameters specified as strings), it prohibited or at least
# made it difficult for us to have our own inheritance hierarchy, we couldn't
# have private fields in our immutable subclasses, we didn't have complete
# control over all methods, type-checking of constructor args involved
# implementing __new__ which was messy, and we had to override __slots__ in
# subclasses to prevent the overhead of a dict (we need to do that with a
# superclass too, but the point is that using this namedtuple thing didn't
# eliminate unnecessary code).
# So we shifted over to subclassing the following Immutable class instead. In
# commit 62 we got rid of all use of the original namedtuple approach, and
# removed that code from this module. 
#
# Good idea for subclasses to override __repr__ and possibly __str__ if they 
# want a shorter friendly string (by default __str__ will just use __repr__).
# Don't worry too much about making __repr__ return something that can be used
# to re-create the object using eval, but since it seems that is the ideal case,
# you might as well use that kind of object-creation format when possible.
# See notes at:
# http://stackoverflow.com/questions/1436703/
class Immutable(object):
    __slots__ = ()
    def _equalityFields(self):
        raise NotImplementedError()
    def __eq__(self, other):
        if self.__class__ != other.__class__:
            return False
        else:
            return self._equalityFields() == other._equalityFields()
    def __ne__(self, other):
        return not (self == other)
    def __hash__(self):
        # For many of our subclasses we get less hash collisions if we include
        # the class type in the hash.  Otherwise, say,
        # DatedBreakdown.daily(Period.latestValues(1)) and
        # DatedBreakdown.monthly(Period.latestValues(1))
        # would have the same hash.
        # We include the class in the hash always for now.  We could of course
        # make it optional later if we wanted to.
        return hash((self.__class__,) + self._equalityFields())

# Rethrowing seems a bit tricky in Python 2.  I initially cobbled together
# something from 
# http://stackoverflow.com/questions/1350671/
# and http://nedbatchelder.com/blog/200711/rethrowing_exceptions_in_python.html
# and a bit of experimentation.
# But then I realized that what I had come up with wouldn't work in Python 3
# because the raise statement had changed - it no longer allowed multiple
# arguments.  So, for commit 66, I came up with this method instead, which works
# on Python 2.5, 2.7 and 3.3, and presumably others in between.
def raiseWrapped(wrapperExceptionClass):
    import sys
    info = sys.exc_info()
    # Note that info[1] is the exception itself.
    newException = wrapperExceptionClass(str(info[0]) + ': ' + str(info[1]))
    try:
        # Try the python 3 way of doing it first:
        newException.with_traceback(info[2])
    except:
        # Need to put below in exec otherwise it won't compile in Python 3.
        exec('raise newException, None, info[2]')
    # If it's got here, with_traceback worked so we just raise that.
    raise newException

# Work out once whether we have viewkeys and viewvalues, as although they say
# exceptions are cheap, they mean the try/except blocks are cheap...  If an
# exception is thrown, it's expensive:
# http://stackoverflow.com/questions/8107695/
def _runHasDictViews():
    testDict = {'key': 5}
    try:
        testDict.viewkeys()
        testDict.viewvalues()
        # It's Python 2, 2.7 or later
        return True
    except:
        # It's either Python 2 before 2.7, or python 3
        return False
_hasDictViews = _runHasDictViews()

def _runHasDictIterMethods():
    testDict = {'key': 5}
    try:
        testDict.iterkeys()
        testDict.itervalues()
        testDict.iteritems()
        # It's Python 2, 2.2 or later.
        return True
    except:
        # It's Python 2 before 2.2 or Python 3
        return False
_hasDictIterMethods = _runHasDictIterMethods()

# This will only work as expected if dictObject won't change.  Otherwise the
# view (python 2.7+ only) will change with it.  Note that viewkeys and
# viewvalues are gone in Python 3, where keys() and values() simply return a
# view instead.
def getSafeDictKeys(dictObject):
    if _hasDictViews:
        return dictObject.viewkeys()
    else:
        return dictObject.keys()
    
def getSafeDictValues(dictObject):
    if _hasDictViews:
        return dictObject.viewvalues()
    else:
        return dictObject.values()
    
def getDictValuesIterable(dictObject):
    if _hasDictIterMethods:
        # Python 2 (2.2 or later) for fast iterating over the values.
        return dictObject.itervalues()
    else:
        # Python 3 by default values returns an iterator.
        return dictObject.values()
    
def getDictItemsIterable(dictObject):
    if _hasDictIterMethods:
        return dictObject.iteritems()
    else:
        # In Python 3, items returns the same as iteritems used to.
        return dictObject.items()
 
# This must calculate the hash of the values in an order-independent way.   
def getDictValuesHash(dictObject, startingHashCode=0):
    hashCode = startingHashCode
    for v in getDictValuesIterable(dictObject):
        # This must be order-independent
        hashCode += hash(v)
    # Before python 2.2 (earlier than this library covers), Python int
    # operations used to result in an error if they got big or small enough
    # to overflow.  They never overflowed automatically like Java ints.
    # Before 3 they automatically turn into longs, after 3 then there is no
    # difference between ints and longs anyway - they're both the int type:
    # http://www.python.org/dev/peps/pep-0237/
    # http://stackoverflow.com/questions/4581842/
    # http://stackoverflow.com/questions/2104884/
    # The docs for __hash__ say it should return an integer, but that, since
    # 2.5 it can return a long, and the system will use the 32-bit hash of
    # that object.  See:
    # http://docs.python.org/2/reference/datamodel.html#object.__hash__
    # To make this work for Python 2.2 to 2.5, we check for int and return
    # the hash if it isn't one (because presumably it's a long).
    # We don't worry about pre-2.2 at all - that may throw an overflow
    # error above.
    if isinstance(hashCode, int):
        return hashCode
    else:
        return hash(hashCode)
    
class Attribute(Immutable):
    __slots__ = ('__name', '__value')
    def __init__(self, name, value):
        self.__name = name
        self.__value = value
    def _equalityFields(self):
        return (self.__name, self.__value)
    @property
    def name(self): return self.__name
    @property
    def value(self): return self.__value
    def appendString(self, s):
        s.append(self.__name)
        s.append("=\"")
        s.append(self.__value)
        s.append("\"")
    
class XmlElement(object):

    def __init__(self, qName):
        # NB below is how you define instance variables in python - if you put
        # them above they're class variables (i.e. like static in Java).
        self.qName = qName
        self.attributes = []
        # can contain XmlElement or string because you can add a string child.
        self.children = []
        self.value = None
    
    def addAttribute(self, name, value):
        self.attributes.append(Attribute(name, str(value)));
        return self;


    def _addChildImpl(self, child):
        if (self.value):
            raise ValueError(
                "Can't have a String value and child elements together")
        self.children.append(child)
        return self
   

    def addXmlStringAsChild(self, xmlString):
        self._addChildImpl(xmlString);
        
    # This returns this, not the child, as coding made it clear that that was
    # more useful.  Don't confuse it with newChild which returns the
    # child.
    def addChild(self, child):
        return self._addChildImpl(child)
        return self

    def newChild(self, qName):
        newChild = XmlElement(qName)
        return self.addChild(newChild)

    def setValue(self, value):
        # check if list is empty
        # http://stackoverflow.com/questions/53513/
        if (self.children):
            raise ValueError(
                    "Can't have child elements and a String value together")
        self.value = str(value)
        return self;

    def appendXmlString(self, stringList):
        stringList.append("<")
        stringList.append(self.qName)
        for a in self.attributes:
            stringList.append(" ")
            a.appendString(stringList)
        if (not self.children and not self.value):
            stringList.append("/>")
        else:
            stringList.append(">")
            if (self.value):
                stringList.append(self.value)
            else:
                for c in self.children:
                    if isinstance(c, XmlElement):
                        c.appendXmlString(stringList)
                    else:
                        stringList.append(c)
            stringList.append("</")
            stringList.append(self.qName)
            stringList.append(">")

    def toXmlString(self):
        # making a list and joining seems to be an efficient way to make a big
        # python string.
        # http://www.skymind.com/~ocrow/python_string/
        stringList = []
        self.appendXmlString(stringList)
        return ''.join(stringList)

# From http://stackoverflow.com/questions/11301138/
try:
    basestring  # attempt to evaluate basestring
    def isString(s):
        return isinstance(s, basestring)
except NameError:
    def isString(s):
        return isinstance(s, str)

def logSafe(string):
    return string # TODO

def __getExampleCode(exampleCodeOrNone):
    if exampleCodeOrNone is None:
        return ''
    else:
        return ' (e.g. ' + exampleCodeOrNone + ')'

def fullNameOfClass(cls):
    # auto-imported classes like str have module __builtin__.  But that's a bit
    # confusing in error messages.  Below is how we test for that, to exclude
    # it.  __module__ can also be None according to the docs.
    if cls.__module__ is None or cls.__module__ == str.__class__.__module__:
        return cls.__name__
    return cls.__module__ + '.' + cls.__name__

def wrongTypeString(param, paramName, expectedType, exampleCodeOrNone=None):
    # str of a type is like <type 'object'>
    return ('%s is an instance of %s, when it should be an instance of %s%s.' % 
        (paramName, fullNameOfClass(param.__class__), 
            fullNameOfClass(expectedType), __getExampleCode(exampleCodeOrNone)))

def wrongSupertypeString(param, paramName, expectedType, 
        exampleCodeOrNone=None):
    return ('%s is an instance of %s, when it should be a subclass of %s%s.' % 
        (paramName, fullNameOfClass(param.__class__), 
            fullNameOfClass(expectedType), __getExampleCode(exampleCodeOrNone)))

# Precompiling doesn't actually make all that much difference, but it is
# faster.
# We're using match to test against this, and match looks for a match at the
# beginning.  So we don't need a ^, but we do need a $ (so as not to match
# a valid string with invalid stuff after it).
_STATION_ID_REGEXP_STRING = '[a-zA-Z0-9_-]{1,60}$' 
_STATION_ID_REGEXP = re.compile(_STATION_ID_REGEXP_STRING)
def checkStationId(stationId, beTolerant):
    if not isString(stationId):
        # Refer to it as 'station ID' - that way this works for methods that
        # take stationId and/or id.
        raise TypeError('The station ID should be a str.')
    if beTolerant:
        stationId = stationId.strip()
    if not _STATION_ID_REGEXP.match(stationId):
        raise ValueError('Invalid station ID (%r) - it should match the '
            'regular expression %s.' %
                (logSafe(stationId), _STATION_ID_REGEXP_STRING))
    return stationId

try:
    intTypes = (int, long)
except:
    # Python 3, where there is no long type.
    intTypes = int
    
try:
    import numbers
    numericTypes = numbers.Number
except:
    # Python 2, before 2.6
    try:
        import decimal
        # Python 2.4 or later
        numericTypes = (int, long, float, decimal.Decimal)
    except:
        # Before Python 2.4
        numercTypes = (int, long, float)
        
try:
    from math import isnan, isinf # if this works we're on 2.6+
except:
    def isnan(number):
        return (number != number)
    # found this worked on Python 2.5 whilst float('inf') did not.
    # At http://stackoverflow.com/questions/2919754/ it says that float('inf')
    # is guaranteed to work on 2.6, but that's pretty much irrelevant since on
    # 2.6 we have math.isinf anyway.
    plusInf = 1e30000
    minusInf = -plusInf
    def isinf(number):
        return (number == plusInf or number == minusInf)

def checkNumeric(param, paramName):
    if not isinstance(param, numericTypes):
        raise TypeError('%s should be a numeric type, but it was of type %s.' %
                        (paramName, fullNameOfClass(param.__class__)))
    elif isnan(param):
        raise ValueError('%s cannot be NaN.' % paramName)
    elif isinf(param):
        raise ValueError('%s cannot be +inf or -inf.' % paramName)
    return param

# This is not tolerant of floats as that could mask bugs.
def checkInt(param, paramName):
    if not isinstance(param, intTypes):
        raise TypeError('%s should be an int, but it was of type %s.' %
            (paramName, fullNameOfClass(param.__class__)))
    return param

def checkString(param, paramName):
    if not isString(param):
        raise TypeError('%s should be a string, but it was of type %s.' %
            (paramName, fullNameOfClass(param.__class__)))
    