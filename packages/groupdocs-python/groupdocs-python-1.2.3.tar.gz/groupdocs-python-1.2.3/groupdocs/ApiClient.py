#!/usr/bin/env python
"""Wordnik.com's Swagger generic API client. This client handles the client-
server communication, and is invariant across implementations. Specifics of
the methods and models for each application are generated from the Swagger
templates."""

from __future__ import print_function
import sys
import os
import re
import urllib
import urllib2
import httplib
import json
import datetime
import mimetypes
import base64

from models import *
from groupdocs.FileStream import FileStream
from groupdocs import version


class RequestSigner(object):
    
    def __init__(self):
        if type(self) == RequestSigner:
            raise Exception("RequestSigner is an abstract class and cannot be instantiated.")
        
    def signUrl(self, url):
        raise NotImplementedError
        
    def signContent(self, requestBody, headers):
        raise NotImplementedError
    

class DefaultRequestSigner(RequestSigner):
    
    def signUrl(self, url):
        return url
        
    def signContent(self, requestBody, headers):
        return requestBody
    
    
class ApiClient(object):
    """Generic API client for Swagger client library builds"""

    def __init__(self, requestSigner=None):
        self.signer = requestSigner if requestSigner != None else DefaultRequestSigner()
        self.cookie = None
        self.headers = {'Groupdocs-Referer': '/'.join((version.__pkgname__, version.__version__))}
        self.__debug = False


    def setDebug(self, flag, logFilepath=None):
        self.__debug = flag
        self.__logFilepath = logFilepath

    def addHeaders(self, **headers):
        self.headers = headers

    def callAPI(self, apiServer, resourcePath, method, queryParams, postData,
                headerParams=None, returnType=str):
        if self.__debug and self.__logFilepath:
            stdOut = sys.stdout
            logFile = open(self.__logFilepath, 'a')
            sys.stdout = logFile

        url = apiServer + resourcePath
        
        headers = {}
        if self.headers:
            for param, value in self.headers.iteritems():
                headers[param] = value
            
        if headerParams:
            for param, value in headerParams.iteritems():
                headers[param] = value

        isFileUpload = False
        if not postData:
            headers['Content-type'] = 'text/html'
        elif isinstance(postData, FileStream):
            isFileUpload = True
            if postData.contentType:
                headers['Content-type'] = postData.contentType
            if postData.size: 
                headers['Content-Length'] = str(postData.size)
        else:
            headers['Content-type'] = 'application/json'

        if self.cookie:
            headers['Cookie'] = self.cookie

        data = None

        if method == 'GET':

            if queryParams:
                # Need to remove None values, these should not be sent
                sentQueryParams = {}
                for param, value in queryParams.items():
                    if value != None:
                        sentQueryParams[param] = value
                if sentQueryParams:
                    url = url + '?' + urllib.urlencode(sentQueryParams)

        elif method in ['POST', 'PUT', 'DELETE']:

            if isFileUpload:
                data = postData.inputStream
            elif not postData:
                data = ""
            elif type(postData) not in [unicode, str, int, float, bool]:
                data = self.signer.signContent(json.dumps(self.sanitizeForSerialization(postData)), headers)
            else: 
                data = self.signer.signContent(postData, headers)

        else:
            raise Exception('Method ' + method + ' is not recognized.')

        if self.__debug:
            handler = urllib2.HTTPSHandler(debuglevel=1) if url.lower().startswith('https') else urllib2.HTTPHandler(debuglevel=1)
            opener = urllib2.build_opener(handler)
            urllib2.install_opener(opener)

        request = MethodRequest(method=method, url=self.encodeURI(self.signer.signUrl(url)), headers=headers,
                                data=data)

        try:
            # Make the request
            response = urllib2.urlopen(request)
            
            if 'Set-Cookie' in response.headers:
                self.cookie = response.headers['Set-Cookie']
        
            if response.code == 200 or response.code == 201 or response.code == 202:
                if returnType == FileStream:
                    fs = FileStream.fromHttp(response)
                    if self.__debug: print(">>>stream info: fileName=%s contentType=%s size=%s" % (fs.fileName, fs.contentType, fs.size))
                    return fs if 'Transfer-Encoding' in response.headers or (fs.size != None and int(fs.size) > 0) else None
                else:                
                    string = response.read()
                    if self.__debug: print(string)
                    try:
                        data = json.loads(string)
                    except ValueError:  # PUT requests don't return anything
                        data = None
                    return data
                
            elif response.code == 404:
                return None
            
            else:
                string = response.read()
                try:
                    msg = json.loads(string)['error_message']
                except ValueError:
                    msg = string
                raise ApiException(response.code, msg)
        except urllib2.HTTPError, e:
            raise ApiException(e.code, e.msg)
                
        finally:
            if isFileUpload:
                try:
                    postData.inputStream.close()
                except Exception, e:
                    sys.exc_clear()
            if self.__debug and self.__logFilepath:
                sys.stdout = stdOut
                logFile.close()
            

    def toPathValue(self, obj):
        """Serialize a list to a CSV string, if necessary.
        
        Args:
            obj -- data object to be serialized
        Returns:
            string -- json serialization of object"""

        if type(obj) == list:
            return ','.join(obj)
        else:
            return obj

    def sanitizeForSerialization(self, obj):
        """Dump an object into JSON for POSTing."""

        if not obj:
            return None
        elif type(obj) in [unicode, str, int, long, float, bool]:
            return obj
        elif type(obj) == list:
            return [self.sanitizeForSerialization(subObj) for subObj in obj]
        elif type(obj) == datetime.datetime:
            return obj.isoformat()
        else:
            if type(obj) == dict:
                objDict = obj
            else:
                objDict = obj.__dict__
            ret_dict = {}
            for (key, val) in objDict.iteritems():
                if key != 'swaggerTypes' and val != None:
                    ret_dict[key] =  self.sanitizeForSerialization(val)
            return ret_dict

    def deserialize(self, obj, objClass):
        """Derialize a JSON string into an object.

        Args:
            obj -- string or object to be deserialized
            objClass -- class literal for deserialzied object, or string of class name
        Returns:
            object -- deserialized object"""

        if not obj:
            return None
            
        # Have to accept objClass as string or actual type. Type could be a
        # native Python type, or one of the model classes.
        if type(objClass) == str:
            if 'list[' in objClass:
                match = re.match('list\[(.*)\]', objClass)
                subClass = match.group(1)
                return [self.deserialize(subObj, subClass) for subObj in obj]

            if (objClass in ['int', 'float', 'long', 'dict', 'list', 'str']):
                objClass = eval(objClass)
            else:  # not a native type, must be model class
                objClass = eval(objClass + '.' + objClass)

        if objClass in [unicode, str, int, long, float, bool]:
            return objClass(obj)
        elif objClass == datetime:
            # Server will always return a time stamp in UTC, but with
            # trailing +0000 indicating no offset from UTC. So don't process
            # last 5 characters.
            return datetime.datetime.strptime(obj[:-5],
                                              "%Y-%m-%dT%H:%M:%S.%f")

        instance = objClass()

        for attr, attrType in instance.swaggerTypes.iteritems():
            lc_attr = attr[0].lower() + attr[1:]
            uc_attr = attr[0].upper() + attr[1:]
            real_attr = None
            if attr in obj:
                real_attr = attr
            elif lc_attr in obj:
                real_attr = lc_attr
            elif uc_attr in obj:
                real_attr = uc_attr
            
            if real_attr != None:
                value = obj[real_attr]
                if not value:
                    setattr(instance, real_attr, None)
                elif attrType in ['str', 'int', 'long', 'float', 'bool']:
                    attrType = eval(attrType)
                    try:
                        value = attrType(value)
                    except UnicodeEncodeError:
                        value = unicode(value)
                    setattr(instance, real_attr, value)
                elif 'list[' in attrType:
                    match = re.match('list\[(.*)\]', attrType)
                    subClass = match.group(1)
                    subValues = []
                    for subValue in value:
                        subValues.append(self.deserialize(subValue,
                                                          subClass))
                    setattr(instance, real_attr, subValues)
                else:
                    setattr(instance, real_attr, self.deserialize(value,
                                                             attrType))

        return instance
    
    @staticmethod
    def encodeURI(url):
        encoded = urllib.quote(url, safe='~@#$&()*!=:;,.?/\'').replace("%25", "%")
        return encoded

    @staticmethod
    def encodeURIComponent(url):
        return urllib.quote(url, safe='~()*!.\'')

    @staticmethod
    def readAsDataURL(filePath):
        mimetype = mimetypes.guess_type(filePath, False)[0] or "application/octet-stream"
        filecontents = open(filePath, 'rb').read()
        return 'data:' + mimetype + ';base64,' + base64.b64encode(filecontents).decode()


class MethodRequest(urllib2.Request):

    def __init__(self, *args, **kwargs):
        """Construct a MethodRequest. Usage is the same as for
        `urllib2.Request` except it also takes an optional `method`
        keyword argument. If supplied, `method` will be used instead of
        the default."""

        if 'method' in kwargs:
            self.method = kwargs.pop('method')
        return urllib2.Request.__init__(self, *args, **kwargs)

    def get_method(self):
        return getattr(self, 'method', urllib2.Request.get_method(self))

class ApiException(Exception):
    def __init__(self, code, *args):
        super(Exception, self).__init__((code, ) + args)
        self.code = code
