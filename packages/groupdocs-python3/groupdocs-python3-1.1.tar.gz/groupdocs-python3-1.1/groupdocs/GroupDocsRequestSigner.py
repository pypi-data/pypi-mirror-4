#!/usr/bin/env python

import urllib.parse
import hmac

from hashlib import sha1
from base64 import b64encode
from .swagger import RequestSigner, ApiClient


class GroupDocsRequestSigner(RequestSigner):
    
    def __init__(self, privateKey):
        self.privateKey = privateKey
        
    def signUrl(self, url):
        urlParts = urllib.parse.urlparse(url)
        pathAndQuery = urlParts.path + ('?' + urlParts.query if urlParts.query else urlParts.query)
        signed = hmac.new(self.privateKey.encode('utf-8'), ApiClient.encodeURI(pathAndQuery).encode('utf-8'), sha1)
        signature = b64encode(signed.digest()).decode('utf-8')
        if signature.endswith("="):
            signature = signature[0 : (len(signature) - 1)]
        url = url + ('&' if urlParts.query else '?') + "signature=" + ApiClient.encodeURIComponent(signature)
        return url
        
    def signContent(self, requestBody, headers):
        return requestBody
    