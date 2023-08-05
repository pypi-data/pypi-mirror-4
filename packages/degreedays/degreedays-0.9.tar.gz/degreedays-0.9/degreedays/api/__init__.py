
from degreedays._private import Immutable
import degreedays._private as private
import string

__all__ = ('AccountKey', 'SecurityKey',
    'Request', 'Response',
    'ResponseMetadata',
    'RateLimit',
    'Failure',
    'FailureResponse',
    'DegreeDaysApiError', 'TransportError', 'FailureError',
    'RequestFailureError', 'InvalidRequestError', 'RateLimitError',
    'ServiceError',
    'DegreeDaysApi')

# lower-case letters apart from i, l, o, and digits apart from 0 and 1.  Doesn't
# include the hyphen which is allowed in certain places.
_KEY_CHARS = frozenset('abcdefghjkmnpqrstuvwxyz23456789')
_UPPER_CASE_KEY_LETTERS = frozenset('ABCDEFGHJKMNPQRSTUVWXYZ')
class _KeyValidator(object):
    def __init__(self, noBlocks, keyName):
        expectedNoHyphens = noBlocks - 1
        self.minLength = (noBlocks * 4)
        self.expectedLength = self.minLength + expectedNoHyphens
        self.noBlocks = noBlocks
        self.keyName = keyName
    def _getValidCharOrNone(self, c):
        if c in _KEY_CHARS:
            return c
        elif c in _UPPER_CASE_KEY_LETTERS:
            return c.lower()
        else:
            return None
    def getValidOrNone(self, s):
        if len(s) < self.minLength:
            return None
        validChars = []
        for c in s:
            validChar = self._getValidCharOrNone(c)
            if validChar is not None:
                length = len(validChars)
                if length >= self.expectedLength:
                    # Too many valid chars means it's invalid
                    return None
                if length > 0 and (length + 1) % 5 == 0:
                    validChars.append('-')
                validChars.append(validChar)
        if len(validChars) != self.expectedLength:
            return None
        return ''.join(validChars)
    def getValidOrThrow(self, s):
        valid = self.getValidOrNone(s)
        if valid is not None:
            return valid
        raise ValueError("Invalid %s - it should be a %d-character string made "
            "up of %d 4-character blocks separated by hyphens.  The 4-character"
            " blocks can contain lower-case Latin alphabet characters apart "
            "from 'i', 'l', and 'o', and numeric digits apart from '0' and "
            "'1'." % (self.keyName, self.expectedLength, self.noBlocks))

_ACCOUNT_KEY_VALIDATOR = _KeyValidator(3, 'stringAccountKey')
class AccountKey(Immutable):
    __slots__ = ('__stringAccountKey')
    def __init__(self, stringAccountKey):
        self.__stringAccountKey = _ACCOUNT_KEY_VALIDATOR.getValidOrThrow(
            stringAccountKey)
    def _equalityFields(self):
        return (self.__stringAccountKey,)
    def __repr__(self):
        return 'AccountKey(%s)' % self.__stringAccountKey
    def __str__(self):
        return self.__stringAccountKey
    @classmethod
    def _check(cls, param, paramName='accountKey'):
        if not isinstance(param, AccountKey):
            raise TypeError(private.wrongTypeString(param, paramName,
                AccountKey, "AccountKey('test-test-test')"))
        return param
    

# TODO - look into security of strings and bytes in Python, and the way that key
# is expected, and think about whether you really want to be storing or
# converting to bytes here.
_SECURITY_KEY_VALIDATOR = _KeyValidator(13, 'stringSecurityKey')
_SECURITY_KEY_EXAMPLE = "SecurityKey('" + ('test-' * 13).rstrip('-') + "')"
class SecurityKey(Immutable):
    __slots__ = ('__bytes')
    def __init__(self, stringSecurityKey):
        stringSecurityKey = _SECURITY_KEY_VALIDATOR.getValidOrThrow(
            stringSecurityKey)
        self.__bytes = stringSecurityKey.encode('utf-8')
    def _equalityFields(self):
        return (self.__bytes,)
    def __repr__(self):
        return 'SecurityKey(string not included for security reasons)'
    def getBytes(self):
        return self.__bytes
    def toStringKey(self):
        return self.__bytes.decode('utf-8')
    @classmethod
    def _check(cls, param, paramName='securityKey'):
        if not isinstance(param, SecurityKey):
            raise TypeError(private.wrongTypeString(param, paramName,
                AccountKey, _SECURITY_KEY_EXAMPLE))
        return param
    
class Request(Immutable):
    __slots__ = ()
    def __init__(self):
        raise TypeError('This is an abstract superclass.  To '
            'create an instance, try creating a LocationDataRequest instead ('
            'LocationDataRequest being a subclass of this).')
    
class RateLimit(Immutable):
    __slots__ = ('__requestUnitsAvailable', '__minutesToReset')
    def __init__(self, requestUnitsAvailable, minutesToReset):
        self.__requestUnitsAvailable = private.checkInt(
            requestUnitsAvailable, 'requestUnitsAvailable')
        self.__minutesToReset = private.checkInt(
            minutesToReset, 'minutesToReset')
        if requestUnitsAvailable < 0:
            raise ValueError('Invalid requestUnitsAvailable (%s) - cannot be '
                '< 0.' % requestUnitsAvailable)
        if minutesToReset < 1:
            raise ValueError('Invalid minutesToReset (%s) - cannot be < 1.' %
                minutesToReset)
    def _equalityFields(self):
        return (self.__requestUnitsAvailable, self.__minutesToReset)
    def __repr__(self):
        return ('RateLimit(requestUnitsAvailable=%d, minutesToReset=%d)' %
            (self.__requestUnitsAvailable, self.__minutesToReset))
    @property
    def requestUnitsAvailable(self): return self.__requestUnitsAvailable
    @property
    def minutesToReset(self): return self.__minutesToReset
    @classmethod
    def _check(cls, param, paramName='rateLimit'):
        if not isinstance(param, RateLimit):
            raise TypeError(private.wrongTypeString(param, paramName,
                RateLimit))
        return param
    
class ResponseMetadata(Immutable):
    __slots__ = ('__rateLimit')
    def __init__(self, rateLimit):
        self.__rateLimit = RateLimit._check(rateLimit)
    def _equalityFields(self):
        return (self.__rateLimit)
    def __repr__(self):
        return 'ResponseMetadata(%r)' % self.__rateLimit
    @property
    def rateLimit(self): return self.__rateLimit
    @classmethod
    def _check(cls, param, paramName='responseMetadata'):
        if not isinstance(param, ResponseMetadata):
            raise TypeError(private.wrongTypeString(param, paramName,
                ResponseMetadata))
        return param
    
class Failure(Immutable):
    __slots__ = ('__code', '__message')
    def __init__(self, code, message):
        self.__code = code
        self.__message = message
    def _equalityFields(self):
        return (self.__code, self.__message)
    def __repr__(self):
        return "Failure('%s', '%s')" % (self.__code, self.__message)
    @property
    def code(self): return self.__code
    @property
    def message(self): return self.__message
    @classmethod
    def _check(cls, param, paramName='failure'):
        if not isinstance(param, Failure):
            raise TypeError(private.wrongTypeString(param, paramName, Failure))
        return param
    
class Response(Immutable):
    __slots__ = ()
    def __init__(self):
        raise TypeError('This is an abstract superclass.  '
            'LocationDataResponse is a subclass that can be instantiated '
            'directly (though typically you would submit a LocationDataRequest '
            'and let the API create the LocationDataResponse automatically).')
    @property
    def metadata(self): raise NotImplementedError()

class FailureResponse(Response):
    __slots__ = ('__metadata', '__failure')
    def __init__(self, metadata, failure):
        self.__metadata = ResponseMetadata._check(metadata, 'metadata')
        self.__failure = Failure._check(failure)
    def _equalityFields(self):
        # metadata is not considered in equality.
        return (self.__failure,)
    def __repr__(self):
        return 'FailureResponse(%r, %r)' % (self.__metadata, self.__failure)
    @property
    def metadata(self): return self.__metadata
    @property
    def failure(self): return self.__failure
    @classmethod
    def _check(cls, param, paramName='failureResponse'):
        if not isinstance(param, FailureResponse):
            raise TypeError(private.wrongTypeString(param, paramName, 
                FailureResponse))
        return param
    
class DegreeDaysApiError(Exception):
    pass

class TransportError(DegreeDaysApiError):
    pass

class FailureError(DegreeDaysApiError):
    def __init__(self, failure):
        self.__failure = Failure._check(failure)
    @property
    def failure(self): return self.__failure
    def _testCode(self, code):
        return self.__failure.code.startswith(code)
    def __str__(self):
        # TODO - check this is working as you'd want if you print the exception
        # or whatever.  Maybe you need the class name in here too?
        return str(self.__failure)

class RequestFailureError(FailureError):
    def __init__(self, failureResponse):
        FailureResponse._check(failureResponse)
        FailureError.__init__(self, failureResponse.failure)
        self.__responseMetadata = failureResponse.metadata
    @property
    def responseMetadata(self):
        return self.__responseMetadata
    @classmethod
    def _create(cls, failureResponse):
        code = failureResponse.failure.code
        if code.startswith('InvalidRequest'):
            return InvalidRequestError(failureResponse);
        elif code.startswith('RateLimit'):
            return RateLimitError(failureResponse);
        elif code.startsWith('Service'):
            return ServiceError(failureResponse);
        else:
            # Shouldn't happen, unless new codes are added in.
            return RequestFailureError(failureResponse)

class InvalidRequestError(RequestFailureError):
    def __init__(self, failureResponse):
        RequestFailureError.__init__(self, failureResponse)
    @property
    def isDueToInvalidRequestAccount(self):
        return self._testCode('InvalidRequestAccount')
    @property
    def isDueToInvalidRequestSignature(self):
        return self._testCode('InvalidRequestSignature')
    @property
    def isDueToInvalidRequestTimestamp(self):
        return self._testCode('InvalidRequestTimestamp')

class RateLimitError(RequestFailureError):
    def __init__(self, failureResponse):
        RequestFailureError.__init__(self, failureResponse)
    @property
    def isDueToRateLimitOnLocationChanges(self):
        return self._testCode('RateLimitOnLocationChanges')

class ServiceError(RequestFailureError):
    def __init__(self, failureResponse):
        RequestFailureError.__init__(self, failureResponse)
    @property
    def isDueToServiceTemporarilyDown(self):
        return self._testCode('ServiceTemporarilyDown')
    @property
    def isDueToServiceUnexpectedError(self):
        return self._testCode('ServiceUnexpectedError') 

class DegreeDaysApi(object):
    def __init__(self, requestProcessor):
        self.__requestProcessor = requestProcessor
        
    @classmethod
    def fromKeys(cls, accountKey, securityKey):
        AccountKey._check(accountKey)
        SecurityKey._check(securityKey)
        # This import must come below the stuff above like FailureResponse and
        # TransportException that _processing imports itself.  Otherwise I guess
        # it makes some sort of circular import issue.  Really this module
        # shouldn't depend on processing, but I think it's OK for the
        # convenience that this method brings.
        from degreedays.api._processing import _buildXmlHttpRequestProcessor
        return DegreeDaysApi(_buildXmlHttpRequestProcessor(
            accountKey, securityKey))
        
    @property
    def dataApi(self):
        from degreedays.api.data import DataApi
        return DataApi(self.__requestProcessor)
