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

import urlparse
import hmac

from hashlib import sha1
from base64 import b64encode
from ApiClient import RequestSigner, ApiClient


class GroupDocsRequestSigner(RequestSigner):
    
    def __init__(self, privateKey):
        self.privateKey = privateKey
        
    def signUrl(self, url):
        urlParts = urlparse.urlparse(url)
        pathAndQuery = urlParts.path + ('?' + urlParts.query if urlParts.query else urlParts.query)
        signed = hmac.new(self.privateKey.encode('utf-8'), ApiClient.encodeURI(pathAndQuery).encode('utf-8'), sha1)
        signature = b64encode(signed.digest()).decode('utf-8')
        if signature.endswith("="):
            signature = signature[0 : (len(signature) - 1)]
        url = url + ('&' if urlParts.query else '?') + "signature=" + ApiClient.encodeURIComponent(signature)
        return url
        
    def signContent(self, requestBody, headers):
        return requestBody
    