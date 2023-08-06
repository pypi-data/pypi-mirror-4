
# Keep this whole package private for the moment.  Think more
# about the design of XmlHttpRequestProcessor before making it public.  For
# example, named parameters are kind of cool, but they don't help us make
# wrappers of existing objects, so in that sense we could rather do with the
# builder pattern.

from threading import Lock
from time import time
from datetime import datetime, timedelta, tzinfo
from degreedays.api import FailureResponse, TransportError
from degreedays._private import * #@UnusedWildImport
from degreedays.api._xmlparsing import DefaultResponseParser
import random

# urllib stuff is different in python 2 and 3.
# We use the approach recommended at http://python3porting.com/noconv.html
try:
    from urllib.request import urlopen, Request
    from urllib.parse import urlencode
except ImportError:
    from urllib2 import urlopen, Request
    from urllib import urlencode
    
import zlib

class HttpRequest(object):
    def __init__(self, url, params):
        self._url = url
        self._params = params.copy()
    @property
    def url(self):
        return self._url
    def paramNames(self):
        return getSafeDictKeys(self._params)
    def getParamValue(self, paramName):
        return self._params[paramName]
    def params(self):
        return self._params.copy()

class RequestSecurityInfo(Immutable):
    __slots__ = ('__endpoint', '__accountKey', '__utcTimestamp',
        '__timestampString', '__random')
    def __init__(self, endpoint, accountKey, utcTimestamp, dateTimeFormatter,
            random):
        self.__endpoint = endpoint
        self.__accountKey = accountKey
        self.__utcTimestamp = utcTimestamp
        self.__timestampString = dateTimeFormatter.format(utcTimestamp)
        self.__random = random
    def _equalityFields(self):
        return (self.__endpoint, self.__accountKey, self.__utcTimestamp,
            self.__timestampString, self.__random)
    @property
    def endpoint(self): return self.__endpoint
    @property
    def accountKey(self): return self.__accountKey
    @property
    def utcTimestamp(self): return self.__utcTimestamp
    @property
    def timestampString(self): return self.__timestampString
    @property
    def random(self): return self.__random
        
class EncodedString(Immutable):
    __slots__ = ('__encoded', '__encoding')
    def __init__(self, encoded, encoding):
        self.__encoded = encoded
        self.__encoding = encoding
    def _equalityFields(self):
        return (self.__encoded, self.__encoding)
    @property
    def encoded(self): return self.__encoded
    @property
    def encoding(self): return self.__encoding

class Signature(Immutable):
    __slots__ = ('__bytes', '__method')
    def __init__(self, bytes, method):
        self.__bytes = bytes
        self.__method = method
    def _equalityFields(self):
        return (self.__bytes, self.__method)
    @property
    def bytes(self): return self.__bytes
    @property
    def method(self): return self.__method
    
    
class DefaultEndpointGetter(object):
    def getEndpoint(self, request):
        return 'http://apiv1.degreedays.net/xml'
    

class DefaultUtcTimestampFactory(object):
    # returns a datetime rather than a time, as a datetime can have better
    # precision.
    def newUtcTimestamp(self):
        return datetime.utcnow()


# Straight from the docs at
# http://docs.python.org/2/library/datetime.html#datetime.tzinfo
# we need this to convert non-UTC times to UTC.
ZERO = timedelta(0)
HOUR = timedelta(hours=1)
# A UTC class.
class UTC(tzinfo):
    """UTC"""
    def utcoffset(self, dt):
        return ZERO
    def tzname(self, dt):
        return "UTC"
    def dst(self, dt):
        return ZERO
utc = UTC()
   

class DefaultDateTimeFormatter(object):
    def format(self, datetime):
        if datetime.tzinfo is not None:
            # It's not a default UTC datetime.
            datetime = datetime.astimezone(utc)
        # isoformat docs say, if datetime.utcoffset() does not return None,
        # it will append a 6-char string like +HH:MM.  We are cautious here in
        # case it appends +00:00 or (perhaps unlikely) -00:00.
        s = datetime.isoformat()
        if (s.endswith('+00:00') or s.endswith('-00:00')):
            s = s[:6] # remove the last 6 characters
        if not s.endswith('Z'):
            s += 'Z'
        return s 

    
class DefaultRandomFactory(object):
    def newRandom(self):
        # this is the method used by the python-oauth2 library, which is
        # supposedly well tested so presumably it works OK.
        return str(random.randint(0, 100000000))
    

class DefaultRequestToXml(object):
    def getXml(self, request):
        return request._toXml().toXmlString()
    

class DefaultXmlRequestWrapper(object):
    def getWrappedXml(self, requestXml, requestSecurityInfo):
        security = XmlElement("SecurityInfo")
        security.addChild(XmlElement("Endpoint").setValue(
                requestSecurityInfo.endpoint))
        security.addChild(XmlElement("AccountKey").setValue(
                str(requestSecurityInfo.accountKey)))
        security.addChild(XmlElement("Timestamp").setValue(
                requestSecurityInfo.timestampString))
        security.addChild(XmlElement("Random").setValue(
                requestSecurityInfo.random))
        envelope = XmlElement("RequestEnvelope")
        envelope.addChild(security)
        envelope.addXmlStringAsChild(requestXml)
        return envelope.toXmlString()
    
    
class DefaultStringToBytes(object):
    def getBytes(self, string):
        # Could do
        # bytearray(string, 'utf-8') which returns a mutable byte array, or
        # bytes(string, 'utf-8') which returns an immutable byte array (bytes
        # object), but I think that's Python 3+ only.
        # Not entirely sure what string.encode returns, but it is recommended
        # at
        # http://stackoverflow.com/questions/7585435/
        return string.encode('utf-8')
        

   
import hmac
import hashlib

class DefaultSigner(object):
    def __init__(self, securityKey):
        self._hmacTemplate = hmac.new(securityKey.getBytes(),
            digestmod=hashlib.sha256)
    # returns bytes
    def getSignature(self, bytesObject):
        # Docs for 2.7.3 say the msg should be a string:
        # http://docs.python.org/2/library/hmac.html
        # Similarly it says it returns a string, though one which may contain
        # null bytes.
        # docs for 3 say msg should be a bytes object and digest returns a bytes
        # object:
        # http://docs.python.org/3.2/library/hmac.html
        # It could be that bytes and strings are pretty much the same thing in
        # earlier python...  I'm not sure...
        hmacObject = self._hmacTemplate.copy()
        # Note instead of this template/copy stuff we could just do the below
        # line.  But the idea was to avoid storing the SecurityKey longer than
        # necessary (as maybe hmac object protects it somehow).
        #hmacObject = hmac.new(self._securityKey.getBytes(), bytesObject, 
        #    hashlib.sha256())
        hmacObject.update(bytesObject)
        return Signature(hmacObject.digest(), 'HmacSHA256')
    
    
import base64
    
class DefaultBytesToEncodedString(object):
    def getEncodedString(self, bytesObject):
        encodedByteString = base64.urlsafe_b64encode(bytesObject)
        encodedString = encodedByteString.decode('utf-8')
        # rstrip('=') below will strip any trailing equals characters (however
        # many there may be).
        encodedString = encodedString.rstrip('=')
        return EncodedString(encodedString, 'base64url')

_oldPython = False
try:    
    from io import RawIOBase
except:
    # probably Python 2.5.  Use a dummy RawIOBase to get the code below to
    # compile, but actually skip all the gzip stuff altogether.  We might be
    # able to get it working, but without RawIOBase or bytearray it looks like
    # it would be pretty tricky.  Perhaps the best we could do would be to
    # load the XML stream into a string in memory and parse that.  But I don't
    # think it's worth bothering with as it's pretty unlikely anyone is using
    # 2.5 anyway.
    _oldPython = True
    class RawIOBase(object):
        pass
    
# Wrapper around a stream containing gzip-compressed content that enables it to
# be read as if it was uncompressed.
class DecompressingStream(RawIOBase):
    def __init__(self, compressedStream, minReadBuffer):
        self._compressed = compressedStream
        self._decompressionObject = zlib.decompressobj(16 + zlib.MAX_WBITS)
        self._minReadBuffer = minReadBuffer
        super(RawIOBase, self).__init__()
    def close(self):
        return self._compressed.close()
    def closed(self):
        return self._compressed.close()
    def fileno(self):
        return self._compressed.fileno  
    def isatty(self):
        return self._compressed.isatty()
    def readable(self):
        return self._compressed.readable()
    # don't allow readline or readlines - just leave it to the superclass to
    # handle those (or probably throw an exception.   
    # can't seek, so leave seek, seekable, tell, and truncate to the superclass
    # (which doesn't allow those by default).
    # similarly for writable, writelines, and flush (only relevant for writable
    # streams).  And also for write (which is a method of BufferedIOBase instead
    # of its superclass IOBase).
    # Now I think we need to implement readinto.  I think RawIOBase handles
    # read, by calling readinto   
    def readinto(self, b):
        toFill = len(b)
        filled = 0
        while filled < toFill:
            tryToFillLength = toFill - filled
            data = None
            if self._decompressionObject.unconsumed_tail:
                data = self._decompressionObject.decompress(
                    self._decompressionObject.unconsumed_tail, tryToFillLength)
            else:
                readFromCompressed = max(tryToFillLength, self._minReadBuffer)
                compressed = self._compressed.read(readFromCompressed)
                data = self._decompressionObject.decompress(
                    compressed, tryToFillLength)
            lengthGot = len(data)
            if lengthGot == 0:
                # Watch out for this...  decompress can return an empty array if
                # we specified a max_length that was too short.  This is
                # particularly likely for the first call, as presumably it has
                # to get past the encoding table or whatever before it can
                # de-compress anything.  But you can also get the same problem
                # later in the stream if you try to decompress chunks that are
                # too small.  So this is why we use _minReadBuffer to ensure
                # that enough data is available for decompression.
                break
            self._hasDecompressed = True
            b[filled:filled + lengthGot] = data
            filled += lengthGot
        return filled
    
    
class DefaultHttpRequestDispatcher(object):
    def dispatch(self, httpRequest):
        try:
            # To handle the gzipped stream we follow the sample at
            # http://rationalpie.wordpress.com/2010/06/02/python-streaming-gzip-decompression/
            dataString = urlencode(httpRequest.params())
            # Python 3 requires the POST data to be bytes.  Should this use
            # StringToBytes?  Maybe, but then also maybe not because this
            # is a conversion that's necessary for the Python urllib library
            # (i.e. required by this particular HttpRequestDispatcher) rather
            # than being something done to satisfy our API specification.
            data = dataString.encode('utf-8')
            # Providing data makes it do a POST instead of a GET.
            request = Request(httpRequest.url, data)
            if not _oldPython:
                request.add_header('Accept-encoding', 'gzip')
            response = urlopen(request)
            isGZipped = response.headers.get(
                'content-encoding', '').find('gzip') >= 0
            if not isGZipped:
                # it's a stream-like object already, and it's decompressed, so
                # we just return it.
                return response
            else:
                return DecompressingStream(response, 1024)
        except Exception:
            raiseWrapped(TransportError)
        
        
class PrintingResponseParser(object):
    def parseResponse(self, responseStream, request):
        # Just a temporary implementation
        s = ''
        while True:
            # Using small reads just for testing.
            read = responseStream.read(6)
            if len(read) == 0:
                break
            else:
                s += read.decode("utf-8")
        print(s)


class RateLimitCache(object):
    _RATE_LIMIT_FAILURE_CACHE_SECONDS = 59.5
    def __init__(self):
        self._lock = Lock()
        self._cachedRateLimitFailureResponse = None
        self._cachedRateLimitFailureSetSeconds = 0

    def getCachedResponseOrNone(self):
        self._lock.acquire()
        try:
            if self._cachedRateLimitFailureResponse is not None:
                nowSeconds = time()
                if nowSeconds < self._cachedRateLimitFailureSetSeconds:
                    # The clock has changed - we don't know what's what and all
                    # we can reasonably do is clear the cached failure.
                    self._cachedRateLimitFailureResponse = None
                elif nowSeconds >= (self._cachedRateLimitFailureSetSeconds +
                        RateLimitCache._RATE_LIMIT_FAILURE_CACHE_SECONDS):
                    self._cachedRateLimitFailureResponse = None
                else:
                    return self._cachedRateLimitFailureResponse
            return None
        finally:
            self._lock.release()
    
    def onFreshResponse(self, response):
        # The check against requestUnitsAvailable is to save an exception
        # being generated unnecessarily each time there's a failure that
        # has nothing to do with the rate limit. Note also that something
        # might fail because of the rate limit, but there might still be
        # request units left if e.g. the request needed 10 request units,
        # but they only had 5. Wouldn't want to cache a response like that,
        # so we test for an available count of zero as well as a rate-limit
        # failure.
        if (isinstance(response, FailureResponse) and
                response.metadata.rateLimit.requestUnitsAvailable == 0):
            code = response.failure.code
            if (code.startswith('RateLimit') and
                    not code.startswith('RateLimitOnLocationChanges')):
                self._lock.acquire()
                try:
                    self._cachedRateLimitFailureResonse = response
                    self._cachedRateLimitFailureSetSeconds = time()
                finally:
                    self._lock.release()

class XmlHttpRequestProcessor(object):
    _lock = Lock() # for accessing the map below
    _rateLimitCacheMap = {}
    # If making this package public we'd want some way to stop this from being
    # called other than by the builder.  Maybe passing the builder in would
    # be the solution.  If we need to add another processing component, we 
    # don't really want optional parameters for those to retain compatibility,
    # as the builder would be neater.
    def __init__(self, accountKey, endpointGetter, utcTimestampFactory,
            dateTimeFormatter, randomFactory, requestToXml, xmlRequestWrapper,
            stringToBytes, signer, bytesToEncodedString, httpRequestDispatcher,
            responseParser):
        self._accountKey = accountKey
        self._endpointGetter = endpointGetter
        self._utcTimestampFactory = utcTimestampFactory
        self._dateTimeFormatter = dateTimeFormatter
        self._randomFactory = randomFactory
        self._requestToXml = requestToXml
        self._xmlRequestWrapper = xmlRequestWrapper
        self._stringToBytes = stringToBytes
        self._signer = signer
        self._bytesToEncodedString = bytesToEncodedString
        self._httpRequestDispatcher = httpRequestDispatcher
        self._responseParser = responseParser
        XmlHttpRequestProcessor._lock.acquire()
        try:
            self._rateLimitCache = \
                XmlHttpRequestProcessor._rateLimitCacheMap.get(accountKey)
            if self._rateLimitCache is None:
                self._rateLimitCache = RateLimitCache()
                XmlHttpRequestProcessor._rateLimitCacheMap[accountKey] = \
                        self._rateLimitCache
        finally:
            XmlHttpRequestProcessor._lock.release()
            
    def _getSecurityInfo(self, endpoint):
        timestamp = self._utcTimestampFactory.newUtcTimestamp()
        return RequestSecurityInfo(endpoint, self._accountKey,
            timestamp, self._dateTimeFormatter,
            self._randomFactory.newRandom())
            
    def _getHttpRequestData(self, request):
        endpoint = self._endpointGetter.getEndpoint(request)
        securityInfo = self._getSecurityInfo(endpoint)
        xml = self._requestToXml.getXml(request)
        wrappedXml = self._xmlRequestWrapper.getWrappedXml(xml, securityInfo)
        xmlBytes = self._stringToBytes.getBytes(wrappedXml)
        signature = self._signer.getSignature(xmlBytes)
        encodedRequest = self._bytesToEncodedString.getEncodedString(xmlBytes)
        # Note python has an immutable bytes type
        encodedSignature = self._bytesToEncodedString.getEncodedString(
            signature.bytes)
        params = {
            'request_encoding' : encodedRequest.encoding,
            'signature_method' : signature.method,
            'signature_encoding' : encodedSignature.encoding,
            'encoded_request' : encodedRequest.encoded,
            'encoded_signature' : encodedSignature.encoded
        }
        return HttpRequest(endpoint, params)
        
    def process(self, request):
        rateLimitCachedResponse = self._rateLimitCache.getCachedResponseOrNone()
        if rateLimitCachedResponse is not None:
            return rateLimitCachedResponse
        httpRequestData = self._getHttpRequestData(request)
        responseStream = self._httpRequestDispatcher.dispatch(httpRequestData)
        isSuccess = False
        try:
            response = None
            try:
                response = self._responseParser.parseResponse(
                    responseStream, request)
            except Exception:
                raiseWrapped(TransportError)
            self._rateLimitCache.onFreshResponse(response)
            isSuccess = True
            return response
        finally:
            if responseStream is not None:
                try:
                    responseStream.close();
                except Exception:
                    if isSuccess:
                        raiseWrapped(TransportError)
                    # otherwise just drop it, as we don't want it replacing the
                    # exception we've had already.
        

# Just a temporary method...  Really we'd want a builder I think.  Just not sure
# how best to do that in Python
def _buildXmlHttpRequestProcessor(accountKey, securityKey):
    return XmlHttpRequestProcessor(
        accountKey,
        DefaultEndpointGetter(),
        DefaultUtcTimestampFactory(),
        DefaultDateTimeFormatter(),
        DefaultRandomFactory(),
        DefaultRequestToXml(),
        DefaultXmlRequestWrapper(),
        DefaultStringToBytes(),
        DefaultSigner(securityKey),
        DefaultBytesToEncodedString(),
        DefaultHttpRequestDispatcher(),
        DefaultResponseParser())