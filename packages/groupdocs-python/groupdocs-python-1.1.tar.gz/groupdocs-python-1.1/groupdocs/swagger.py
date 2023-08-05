#!/usr/bin/env python
"""Wordnik.com's Swagger generic API client. This client handles the client-
server communication, and is invariant across implementations. Specifics of
the methods and models for each application are generated from the Swagger
templates."""

import sys
import os
import re
import urllib
import urllib2
import httplib
import json
import datetime
import mimetypes

from models import *


class RequestSigner(object):
    
    def __init__(self):
        if type(self) == RequestSigner:
            raise Exception("RequestSigner is an abstract class and cannot be instantiated.")
        
    def signUrl(self, url):
        raise NotImplementedError
        
    def signContent(self, requestBody, headers):
        raise NotImplementedError
    

class DefaultRequestSigner(RequestSigner):
    
    def __init__(self, apiKey):
        self.apiKey = apiKey
        
    def signUrl(self, url):
        return url
        
    def signContent(self, requestBody, headers):
        return requestBody
    
    
class ApiClient:
    """Generic API client for Swagger client library builds"""

    def __init__(self, apiKey=None, apiServer=None, requestSigner=DefaultRequestSigner):
        if apiKey == None:
            raise Exception('You must pass an apiKey when instantiating the '
                            'APIClient')
        self.signer = requestSigner(apiKey)
        self.apiServer = apiServer
        self.cookie = None

    def callAPI(self, resourcePath, method, queryParams, postData,
                headerParams=None):

        url = self.apiServer + resourcePath
        headers = {}
        if headerParams:
            for param, value in headerParams.iteritems():
                headers[param] = value

        if type(self.signer) == DefaultRequestSigner:
            headers['api_key'] = self.signer.apiKey
        
        filename = False
        if not postData:
            headers['Content-type'] = 'text/html'
        elif isinstance(postData, str) and postData.startswith('file://'):
            filename = postData[7:len(postData)]
            headers['Content-type'] = mimetypes.guess_type(filename)[0] or 'application/octet-stream'
            headers['Content-Length'] = str(os.path.getsize(filename))
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
                url = url + '?' + urllib.urlencode(sentQueryParams)

        elif method in ['POST', 'PUT', 'DELETE']:

            if filename:
                data = open(filename, "rb")
            elif type(postData) not in [str, int, float, bool]:
                data = self.signer.signContent(json.dumps(self.sanitizeForSerialization(postData)), headers)
            else: 
                data = self.signer.signContent(postData, headers)

        else:
            raise Exception('Method ' + method + ' is not recognized.')

        request = MethodRequest(method=method, url=self.encodeURI(self.signer.signUrl(url)), headers=headers,
                                data=data)

        # Make the request
        response = urllib2.urlopen(request)
        if 'Set-Cookie' in response.headers:
            self.cookie = response.headers['Set-Cookie']
        string = response.read()

        try:
            data = json.loads(string)
        except ValueError:  # PUT requests don't return anything
            data = None

        return data

    def toPathValue(self, obj):
        """Serialize a list to a CSV string, if necessary.
        Args:
            obj -- data object to be serialized
        Returns:
            string -- json serialization of object
        """
        if type(obj) == list:
            return ','.join(obj)
        else:
            return obj

    def sanitizeForSerialization(self, obj):
        """Dump an object into JSON for POSTing."""

        if not obj:
            return None
        elif type(obj) in [str, int, long, float, bool]:
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
            return {key: self.sanitizeForSerialization(val)
                    for (key, val) in objDict.iteritems()
                    if key != 'swaggerTypes' and val != None}

    def deserialize(self, obj, objClass):
        """Derialize a JSON string into an object.

        Args:
            obj -- string or object to be deserialized
            objClass -- class literal for deserialzied object, or string
                of class name
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

        if objClass in [str, int, long, float, bool]:
            return objClass(obj)
        elif objClass == datetime:
            # Server will always return a time stamp in UTC, but with
            # trailing +0000 indicating no offset from UTC. So don't process
            # last 5 characters.
            return datetime.datetime.strptime(obj[:-5],
                                              "%Y-%m-%dT%H:%M:%S.%f")

        instance = objClass()

        for attr, attrType in instance.swaggerTypes.iteritems():
            if attr in obj:
                value = obj[attr]
                if attrType in ['str', 'int', 'long', 'float', 'bool']:
                    attrType = eval(attrType)
                    try:
                        value = attrType(value)
                    except UnicodeEncodeError:
                        value = unicode(value)
                    setattr(instance, attr, value)
                elif 'list[' in attrType:
                    match = re.match('list\[(.*)\]', attrType)
                    subClass = match.group(1)
                    subValues = []
                    if not value:
                        setattr(instance, attr, None)
                    else:
                        for subValue in value:
                            subValues.append(self.deserialize(subValue,
                                                              subClass))
                    setattr(instance, attr, subValues)
                else:
                    setattr(instance, attr, self.deserialize(value,
                                                             attrType))

        return instance
    
    @staticmethod
    def encodeURI(url):
        encoded = urllib.quote(url, safe='~@#$&()*!=:;,.?/\'').replace("%25", "%")
        return encoded

    @staticmethod
    def encodeURIComponent(url):
        return urllib.quote(url, safe='~()*!.\'')


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

