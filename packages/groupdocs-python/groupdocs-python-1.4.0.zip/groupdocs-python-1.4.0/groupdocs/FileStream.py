#!/usr/bin/env python
"""
Copyright 2012 GroupDocs.

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
"""
import os
import mimetypes
import urlparse

class FileStream(object):
    """This class encapsulates data needed either for file upload or download. All properties are initialized lazily on first access.
    
    To use this class for file upload initialize it with absolute path to file on your filesystem.
    
    To use this class for file download call fromHttp(response) method.
    """
    
    def __init__(self, filePath=None, response=None, stream=None):
        self.__response = response # used for file download
        self.__filePath = filePath # used for file upload
        self.__fileName = None
        self.__contentType = None
        self.__size = None
        self.__inputStream = stream
            
    @classmethod
    def fromFile(cls, filePath):
        """filePath is an absolute path to file on your filesystem.
        """
        return cls(filePath, None)
    
    @classmethod
    def fromStream(cls, stream, size, contentType="application/octet-stream"):
        """stream is a file-like object, i.e. stream = fopen(filename)
        """
        if not size or int(size) <= 0:
            raise ValueError('Invalid stream size provided')
        
        instance = cls(None, None, stream)
        instance.size = size
        instance.contentType = contentType
        return instance
    
    @classmethod
    def fromHttp(cls, response):
        """response is a file-like object with two additional methods: geturl() and info()
        """
        return cls(None, response)
    
    @property
    def fileName(self):
        if self.__fileName == None and self.__filePath != None:
            self.__fileName = os.path.basename(self.__filePath)
        elif self.__fileName == None and self.__response != None:
            self.__fileName = self.__getValueFromCD('filename') or self.__getFileNameFromUrl(self.__response.url)
        return self.__fileName
    
    @fileName.setter
    def fileName(self, value):
        self.__fileName = value

    @property
    def contentType(self):
        if self.__contentType == None and self.__filePath != None:
            self.__contentType = mimetypes.guess_type(self.__filePath)[0] or "application/octet-stream"
        elif self.__contentType == None and self.__response != None:
            self.__contentType = self.__response.info()['Content-Type'] if 'Content-Type' in self.__response.info() else None
        return self.__contentType
    
    @contentType.setter
    def contentType(self, value):
        self.__contentType = value

    @property
    def size(self):
        if self.__size == None and self.__filePath != None:
            self.__size = os.path.getsize(self.__filePath)
        elif self.__size == None and self.__response != None:
            self.__size = self.__getValueFromCD('size')
            if self.__size == None and 'Content-Length' in self.__response.info():
                self.__size = self.__response.info()['Content-Length'] 
        return self.__size
    
    @size.setter
    def size(self, value):
        self.__size = value

    @property
    def inputStream(self):
        """returns file object
        """
        if self.__inputStream == None and self.__filePath != None:
            self.__inputStream = open(self.__filePath, "rb")
        elif self.__inputStream == None and self.__response != None:
            self.__inputStream = self.__response
        return self.__inputStream
    
    @inputStream.setter
    def inputStream(self, value):
        self.__inputStream = value
        
    def __getValueFromCD(self, key):
        headers = self.__response.info()
        if 'Content-Disposition' in headers:
            # If the response has Content-Disposition, try to get value from it
            cd = dict(map(
                lambda x: x.strip().split('=') if '=' in x else (x.strip(),''),
                headers['Content-Disposition'].split(';')))
            if key in cd:
                value = cd[key].strip("\"'")
                if value: return value
        return None
    
    def __getFileNameFromUrl(self, url):
        return os.path.basename(urlparse.urlsplit(url)[2])
        
