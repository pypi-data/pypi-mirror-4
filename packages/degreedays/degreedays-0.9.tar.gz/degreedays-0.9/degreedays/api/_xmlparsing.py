
from xml.sax import ContentHandler, parse
from degreedays.api import * #@UnusedWildImport
from degreedays.api.data import * #@UnusedWildImport
from degreedays.geo import * #@UnusedWildImport
from degreedays.time import * #@UnusedWildImport
import datetime

# Don't actually use this - just take a function.
class CollectionCallback(object):
    def collectionEnded(self, collected):
        pass
    
class DelegateLifetime(object):
    def onStart(self, qName, attributes):
        pass
    def isEnd(self, qName):
        pass
    
class SimpleDelegateLifetime(DelegateLifetime):
    def __init__(self, qName):
        self.__qName = qName
        self.__count = 1
    def isEnd(self, qName):
        if self.__qName == qName:
            self.__count -= 1
            if self.__count == 0:
                return True
        return False
    def onStart(self, qName, attributes):
        if self.__qName == qName:
            self.__count += 1
    
class CharacterCollectionStrategy(object):
    # Return none if it doesn't want the characters for this qName
    def getCollectionCallbackOrNone(self, qName, attributes):
        pass
    
class FixedCharacterCollectionStrategy(CharacterCollectionStrategy):
    def __init__(self, nameSet):
        self.__nameSet = nameSet
        self.__nameToCollectedStringMap = {}
    def getCollectionCallbackOrNone(self, qName, attributes):
        if qName in self.__nameSet:
            def callback(collected):
                self.__nameToCollectedStringMap[qName] = collected
            return callback
        else:
            return None
    def getCollectedOrNone(self, qName):
        return self.__nameToCollectedStringMap.get(qName)


class SimpleSaxHandler(ContentHandler):
    
    def __init__(self):
        ContentHandler.__init__(self)
        self.__delegateHandlingEndedCallback = None
        self.__parent = None
        self.__childDelegates = []
        self.__childDelegateLifetimes = []
        self.__currentDelegate = None
        self.__currentDelegateLifetime = None
        self.__characterCollectionStrategy = None
        # Following are non None if characters are being collected.  Then back
        # to None when we're done.
        self.__collectionCallbackOrNone = None
        self.__characterCollector = None
        
    def withDelegateHandlingEndedCallback(self, callback):
        self.__delegateHandlingEndedCallback = callback
        return self
    
    def setCharacterCollectionStrategy(self, strategy):
        self.__characterCollectionStrategy = strategy
        return strategy
    
    def __getRootAncestor(self):
        testHandler = self
        while testHandler.__parent is not None:
            testHandler = testHandler.__parent
        return testHandler
        
    def startElement(self, qName, attributes):
        if self.__currentDelegate is not None:
            self.__currentDelegateLifetime.onStart(qName, attributes)
            self.__currentDelegate.startElement(qName, attributes)
        else:
            if self.__characterCollectionStrategy is not None:
                callbackOrNone = self.__characterCollectionStrategy \
                    .getCollectionCallbackOrNone(qName, attributes)
                if callbackOrNone is not None:
                    self.collectCharacters(callbackOrNone)
            self.startElementImpl(qName, attributes)
     
    def startElementImpl(self, qName, attributes):
        pass
     
    def endElement(self, qName):
        isDelegated = False
        if self.__currentDelegate is not None:
            if self.__currentDelegateLifetime.isEnd(qName):
                self.__currentDelegate.delegateHandlingEnded()
                noParents = len(self.__childDelegates)
                if noParents > 0:
                    self.__currentDelegate = self.__childDelegates.pop()
                    self.__currentDelegateLifetime = \
                        self.__childDelegateLifetimes.pop() 
                else:
                    self.__currentDelegate = None
                    self.__currentDelegateLifetime = None
            else:
                self.__currentDelegate.endElement(qName)
                isDelegated = True
        if not isDelegated:
            if self.__collectionCallbackOrNone is not None:
                collected = ''.join(self.__characterCollector)
                self.__collectionCallbackOrNone(collected)
                # reset now to save memory.
                self.__characterCollector = None
                # Set to null so we know not to collect more.
                self.__collectionCallbackOrNone = None
            self.endElementImpl(qName);
    
    def endElementImpl(self, qName):
        pass
    
    def addDelegate(self, delegate, lifetimeOrQNameForEnd):
        delegate.__parent = self
        root = self.__getRootAncestor()
        if not isinstance(lifetimeOrQNameForEnd, DelegateLifetime):
            lifetimeOrQNameForEnd = \
                SimpleDelegateLifetime(lifetimeOrQNameForEnd)
        root.__addDelegateImpl(delegate, lifetimeOrQNameForEnd)
    
    def __addDelegateImpl(self, delegate, lifetime):
        if (self.__currentDelegate is not None):
            self.__childDelegates.append(self.__currentDelegate)
            self.__childDelegateLifetimes.append(self.__currentDelegateLifetime)
        self.__currentDelegate = delegate
        self.__currentDelegateLifetime = lifetime
    
    # Subclasses can override this if they want to be told when they are no
    # longer the delegate handler.  Override this to get the completed stuff
    # out of a delegate when it's done.
    def delegateHandlingEnded(self):
        if self.__delegateHandlingEndedCallback is not None:
            self.__delegateHandlingEndedCallback(self)
    
    # To be called by a subclass in {@link #startElementImpl}.  Probably 
    # unnecessary to call this if using a {@link CharacterCollectionStrategy}.
    def collectCharacters(self, collectionCallback):
        self.__characterCollector = []
        self.__collectionCallbackOrNone = collectionCallback;
    
    def characters(self, content):
        if self.__currentDelegate is not None:
            self.__currentDelegate.characters(content)
        elif self.__collectionCallbackOrNone is not None:
            self.__characterCollector.append(content)

REQUEST_UNITS_AVAILABLE = 'RequestUnitsAvailable'
MINUTES_TO_RESET = 'MinutesToReset'
# set and frozenset were both introduced in Python 2.4.  So there's no reason
# to use set when frozenset is better here (as it's immutable).
RATE_LIMIT_NAMES = frozenset((REQUEST_UNITS_AVAILABLE, MINUTES_TO_RESET))

class SaxHandlerForRateLimit(SimpleSaxHandler):
    def __init__(self):
        SimpleSaxHandler.__init__(self)
        self.chars = self.setCharacterCollectionStrategy(
            FixedCharacterCollectionStrategy(RATE_LIMIT_NAMES))
    def getRateLimit(self):
        requestUnits = int(self.chars.getCollectedOrNone(
            REQUEST_UNITS_AVAILABLE))
        minutesToReset = int(self.chars.getCollectedOrNone(
            MINUTES_TO_RESET))
        return RateLimit(requestUnits, minutesToReset)
    
class SaxHandlerForResponseMetadata(SimpleSaxHandler):
    def startElementImpl(self, qName, attributes):
        if "RateLimit" == qName:
            def callback(handler):
                self.rateLimit = handler.getRateLimit()
            self.addDelegate(SaxHandlerForRateLimit() \
                .withDelegateHandlingEndedCallback(callback), qName)
    def getMetadata(self):
        return ResponseMetadata(self.rateLimit)

CODE = 'Code'
MESSAGE = 'Message'
FAILURE_NAMES = frozenset((CODE, MESSAGE))
    
class SaxHandlerForFailure(SimpleSaxHandler):
    def __init__(self):
        SimpleSaxHandler.__init__(self)
        self.chars = self.setCharacterCollectionStrategy(
            FixedCharacterCollectionStrategy(FAILURE_NAMES))
    def getFailure(self):
        return Failure(
            self.chars.getCollectedOrNone(CODE),
            self.chars.getCollectedOrNone(MESSAGE))
        
class SaxHandlerForFailureResponse(SaxHandlerForFailure):
    def getResponse(self, metadata):
        return FailureResponse(metadata, self.getFailure())
    
def parseLongLat(attributes):
    return LongLat(float(attributes.getValue('longitude')),
        float(attributes.getValue('latitude')))

def parseMetresDistance(distanceString):
    return Distance.metres(float(distanceString))
   
# Could put this in time module, but not sure we want to commit to keeping it.
def parseIsoDate(dateString):
    split = dateString.split('-', 2)
    return datetime.date(int(split[0]), int(split[1]), int(split[2]))

def parsePercentageEstimated(peString):
    return float(peString)

def parsePercentageEstimatedAttribute(attributes):
    if 'pe' in attributes:
        return float(attributes.getValue('pe'))
    else:
        return 0.0

def parseDegreeDayValue(valueString):
    return float(valueString)

class SaxHandlerForTargetLocation(SimpleSaxHandler):
    def startElementImpl(self, qName, attributes):
        if 'LongLat' == qName:
            self.longLat = parseLongLat(attributes)

ID = 'Id'
ELEVATION_METRES = 'ElevationMetres'
DISPLAY_NAME = 'DisplayName'
STATION_NAMES = frozenset((ID, ELEVATION_METRES, DISPLAY_NAME))
class SaxHandlerForStation(SimpleSaxHandler):
    def __init__(self):
        SimpleSaxHandler.__init__(self)
        self.chars = self.setCharacterCollectionStrategy(
            FixedCharacterCollectionStrategy(STATION_NAMES))
    def startElementImpl(self, qName, attributes):
        if 'LongLat' == qName:
            self.longLat = parseLongLat(attributes)
    def getStation(self):
        return Station(
            self.chars.getCollectedOrNone(ID),
            self.longLat,
            parseMetresDistance(
                self.chars.getCollectedOrNone(ELEVATION_METRES)),
            self.chars.getCollectedOrNone(DISPLAY_NAME))  

METRES_FROM_TARGET = 'MetresFromTarget'
SOURCE_NAMES = frozenset((METRES_FROM_TARGET,))
class SaxHandlerForSource(SimpleSaxHandler):
    def __init__(self):
        SimpleSaxHandler.__init__(self)
        self.chars = self.setCharacterCollectionStrategy(
            FixedCharacterCollectionStrategy(SOURCE_NAMES))
    def startElementImpl(self, qName, attributes):
        if 'Station' == qName:
            def callback(handler):
                self.station = handler.getStation()
            self.addDelegate(SaxHandlerForStation() \
                .withDelegateHandlingEndedCallback(callback), qName)
    def getSource(self):
        return Source(self.station, parseMetresDistance(
            self.chars.getCollectedOrNone(METRES_FROM_TARGET)))

class SaxHandlerForSources(SimpleSaxHandler):
    def __init__(self):
        SimpleSaxHandler.__init__(self)
        self.sources = []
    def startElementImpl(self, qName, attributes):
        if 'Source' == qName:
            def callback(handler):
                self.sources.append(handler.getSource())
            self.addDelegate(SaxHandlerForSource() \
                .withDelegateHandlingEndedCallback(callback), qName)
   
STATION_ID = "StationId"
LOCATION_DATA_RESPONSE_HEAD_NAMES = frozenset((STATION_ID,))
class SaxHandlerForLocationDataResponseHead(SimpleSaxHandler):
    def __init__(self):
        SimpleSaxHandler.__init__(self)
        self.chars = self.setCharacterCollectionStrategy(
            FixedCharacterCollectionStrategy(LOCATION_DATA_RESPONSE_HEAD_NAMES))
    def startElementImpl(self, qName, attributes):
        if 'TargetLocation' == qName:
            def callback(handler):
                self.targetLongLat = handler.longLat
            self.addDelegate(SaxHandlerForTargetLocation() \
                .withDelegateHandlingEndedCallback(callback), qName)
        elif 'Sources' == qName:
            def callback(handler):
                self.sources = handler.sources
            self.addDelegate(SaxHandlerForSources() \
                .withDelegateHandlingEndedCallback(callback), qName)
    def fillDict(self, d):
        d['stationId'] = self.chars.getCollectedOrNone(STATION_ID)
        d['targetLongLat'] = self.targetLongLat
        d['sources'] = self.sources

PERCENTAGE_ESTIMATED = 'PercentageEstimated'
DATED_DATA_SET_HEAD_NAMES = frozenset((PERCENTAGE_ESTIMATED,))

class SaxHandlerForDatedDataSetHead(SimpleSaxHandler):
    def __init__(self):
        SimpleSaxHandler.__init__(self)
        self.chars = self.setCharacterCollectionStrategy(
            FixedCharacterCollectionStrategy(DATED_DATA_SET_HEAD_NAMES))
    def fillDict(self, d):
        d['percentageEstimated'] = parsePercentageEstimated(
            self.chars.getCollectedOrNone(PERCENTAGE_ESTIMATED))

class SaxHandlerForDatedDataSetValues(SimpleSaxHandler):
    def __init__(self):
        SimpleSaxHandler.__init__(self)
        self.setCharacterCollectionStrategy(self)
        self.datedDataValues = []
    def getCollectionCallbackOrNone(self, qName, attributes):
        if qName != 'V':
            return None
        firstDay = parseIsoDate(attributes.getValue('d'))
        if 'ld' in attributes:
            lastDay = parseIsoDate(attributes.getValue('ld'))
            self.dayRange = DayRange(firstDay, lastDay)
        else:
            self.dayRange = DayRange.singleDay(firstDay)
        self.percentageEstimated = parsePercentageEstimatedAttribute(attributes)
        return self.collectionEnded
    def collectionEnded(self, collected):
        value = parseDegreeDayValue(collected)
        datedDataValue = DatedDataValue(
            value, self.percentageEstimated, self.dayRange)
        self.datedDataValues.append(datedDataValue)
       
class SaxHandlerForDatedDataSet(SimpleSaxHandler):
    def __init__(self):
        SimpleSaxHandler.__init__(self)
        self.params = {}
    def startElementImpl(self, qName, attributes):
        if 'Head' == qName:
            def callback(handler):
                handler.fillDict(self.params)
            self.addDelegate(SaxHandlerForDatedDataSetHead() \
                .withDelegateHandlingEndedCallback(callback), qName)
        elif 'Values' == qName:
            def callback(handler):
                self.params['values'] = handler.datedDataValues
            self.addDelegate(SaxHandlerForDatedDataSetValues() \
                .withDelegateHandlingEndedCallback(callback), qName)
    def getResult(self):
        return DatedDataSet(**self.params)

FIRST_YEAR = 'FirstYear'
LAST_YEAR = 'LastYear'
AVERAGE_DATA_SET_HEAD_NAMES = frozenset((FIRST_YEAR, LAST_YEAR))   
class SaxHandlerForAverageDataSetHead(SimpleSaxHandler):
    def __init__(self):
        SimpleSaxHandler.__init__(self)
        self.chars = self.setCharacterCollectionStrategy(
            FixedCharacterCollectionStrategy(AVERAGE_DATA_SET_HEAD_NAMES))
    def fillDict(self, d):
        d['firstYear'] = int(self.chars.getCollectedOrNone(FIRST_YEAR))
        d['lastYear'] = int(self.chars.getCollectedOrNone(LAST_YEAR))
        
class SaxHandlerForAverageDataSetMonthlyValues(SimpleSaxHandler):
    def __init__(self):
        SimpleSaxHandler.__init__(self)
        self.setCharacterCollectionStrategy(self)
        self.monthlyAverages = []
    def getCollectionCallbackOrNone(self, qName, attributes):
        if qName != 'M':
            return None
        self.percentageEstimated = parsePercentageEstimatedAttribute(attributes)
        return self.collectionEnded
    def collectionEnded(self, collected):
        value = parseDegreeDayValue(collected)
        dataValue = DataValue(value, self.percentageEstimated)
        self.monthlyAverages.append(dataValue)
        
class SaxHandlerForAverageDataSetValues(SimpleSaxHandler):
    def startElementImpl(self, qName, attributes):
        if 'Monthly' == qName:
            def callback(handler):
                self.monthlyAverages = handler.monthlyAverages
            self.addDelegate(SaxHandlerForAverageDataSetMonthlyValues() \
                .withDelegateHandlingEndedCallback(callback), qName)
        elif 'Annual' == qName:
            percentageEstimated = parsePercentageEstimatedAttribute(attributes)
            def collectionEnded(collected):
                value = parseDegreeDayValue(collected)
                self.annualAverage = DataValue(value, percentageEstimated)
            self.collectCharacters(collectionEnded)

class SaxHandlerForAverageDataSet(SimpleSaxHandler):
    def __init__(self):
        SimpleSaxHandler.__init__(self)
        self.params = {}
    def startElementImpl(self, qName, attributes):
        if 'Head' == qName:
            def callback(handler):
                handler.fillDict(self.params)
            self.addDelegate(SaxHandlerForAverageDataSetHead() \
                .withDelegateHandlingEndedCallback(callback), qName)
        elif 'Values' == qName:
            def callback(handler):
                self.params['annualAverage'] = handler.annualAverage
                self.params['monthlyAverages'] = handler.monthlyAverages
            self.addDelegate(SaxHandlerForAverageDataSetValues() \
                .withDelegateHandlingEndedCallback(callback), qName)
    def getResult(self):
        return AverageDataSet(**self.params)

class SaxHandlerForDataSetFailure(SaxHandlerForFailure):
    def getResult(self):
        return self.getFailure()
        
class SaxHandlerForDataSets(SimpleSaxHandler):
    def __init__(self):
        SimpleSaxHandler.__init__(self)
        self.resultsMap = {}
    def __addHandler(self, qName, attributes, newHandler):
        def callback(handler):
            self.resultsMap[attributes.getValue('key')] = handler.getResult()
        newHandler = newHandler.withDelegateHandlingEndedCallback(callback)
        self.addDelegate(newHandler, qName)    
    def startElementImpl(self, qName, attributes):
        if 'DatedDataSet' == qName:
            self.__addHandler(qName, attributes, SaxHandlerForDatedDataSet())
        elif 'AverageDataSet' == qName:
            self.__addHandler(qName, attributes, SaxHandlerForAverageDataSet())
        elif 'Failure' == qName:
            self.__addHandler(qName, attributes, SaxHandlerForDataSetFailure())
    def getDataSets(self, dataSpecsOrNone):
        return DataSets(dataSpecsOrNone, self.resultsMap)
    
class SaxHandlerForLocationDataResponse(SimpleSaxHandler):
    def __init__(self, locationDataRequestOrNone):
        SimpleSaxHandler.__init__(self)
        if locationDataRequestOrNone is None:
            self.dataSpecsOrNone = None
        else:
            self.dataSpecsOrNone = locationDataRequestOrNone.dataSpecs
        self.params = {}
    def startElementImpl(self, qName, attributes):
        if 'Head' == qName:
            def callback(handler):
                handler.fillDict(self.params)
            self.addDelegate(SaxHandlerForLocationDataResponseHead() \
                .withDelegateHandlingEndedCallback(callback), qName)
        elif 'DataSets' == qName:
            def callback(handler):
                self.params['dataSets'] = handler.getDataSets(
                    self.dataSpecsOrNone)
            self.addDelegate(SaxHandlerForDataSets() \
                .withDelegateHandlingEndedCallback(callback), qName)
    def getResponse(self, metadata):
        self.params['metadata'] = metadata
        return LocationDataResponse(**self.params)

class SaxHandlerForResponse(SimpleSaxHandler):
    def __init__(self, requestOrNone):
        SimpleSaxHandler.__init__(self)
        self.requestOrNone = requestOrNone
    def startElementImpl(self, qName, attributes):
        if 'Metadata' == qName:
            def callback(handler):
                self.metadata = handler.getMetadata()
            self.addDelegate(SaxHandlerForResponseMetadata() \
                .withDelegateHandlingEndedCallback(callback), qName)
        elif 'LocationDataResponse' == qName:
            def callback(handler):
                self.response = handler.getResponse(self.metadata)
            self.addDelegate(
                SaxHandlerForLocationDataResponse(self.requestOrNone) \
                    .withDelegateHandlingEndedCallback(callback), qName)
        elif 'Failure' == qName:
            def callback(handler):
                self.response = handler.getResponse(self.metadata)
            self.addDelegate(SaxHandlerForFailureResponse() \
                .withDelegateHandlingEndedCallback(callback), qName)     
            
class DefaultResponseParser(object):
    def parseResponse(self, responseStream, request):
        handler = SaxHandlerForResponse(request)
        parse(responseStream, handler)
        return handler.response
        