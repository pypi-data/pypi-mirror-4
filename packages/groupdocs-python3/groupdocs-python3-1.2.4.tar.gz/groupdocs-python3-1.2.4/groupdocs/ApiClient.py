#!/usr/bin/env python
"""Wordnik.com's Swagger generic API client. This client handles the client-
server communication, and is invariant across implementations. Specifics of
the methods and models for each application are generated from the Swagger
templates."""

import sys
import os
import re
import urllib.request, urllib.parse, urllib.error
import http.client
import json
import datetime
import mimetypes
import base64

from .models import *
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
            for param, value in self.headers.items():
                headers[param] = value
            
        if headerParams:
            for param, value in headerParams.items():
                headers[param] = value

        isFileUpload = False
        if not postData:
            headers['Content-type'] = 'text/html'
        elif isinstance(postData, FileStream):
            isFileUpload = True
            if postData.contentType:
                headers['Content-type'] = 'application/octet-stream'
            if postData.size: 
                headers['Content-Length'] = str(postData.size)
        else:
            headers['Content-type'] = 'application/json'

        if self.cookie:
            headers['Cookie'] = self.cookie

        data = None

        if queryParams:
            # Need to remove None values, these should not be sent
            sentQueryParams = {}
            for param, value in queryParams.items():
                if value != None:
                    sentQueryParams[param] = value
            if sentQueryParams:
                url = url + '?' + urllib.parse.urlencode(sentQueryParams)

        if method in ['POST', 'PUT', 'DELETE']:

            if isFileUpload:
                data = postData.inputStream
            elif not postData:
                data = ""
            elif type(postData) not in [str, int, float, bool]:
                data = self.signer.signContent(json.dumps(self.sanitizeForSerialization(postData)), headers)
            else: 
                data = self.signer.signContent(postData, headers)

        if self.__debug:
            http.client.HTTPConnection.debuglevel = 1
            
        if data and not isFileUpload:
            data = data.encode('utf-8')

        request = MethodRequest(method=method, url=self.encodeURI(self.signer.signUrl(url)), headers=headers,
                                data=data)

        try:
            # Make the request
            response = urllib.request.urlopen(request)
            
            if 'Set-Cookie' in response.headers:
                self.cookie = response.headers['Set-Cookie']
        
            if response.code == 200 or response.code == 201 or response.code == 202:
                if returnType == FileStream:
                    fs = FileStream.fromHttp(response)
                    if self.__debug: print("\n", "< Response Body:\n", ">>>stream info: fileName=%s contentType=%s size=%s" % (fs.fileName, fs.contentType, fs.size), "\n", sep="")
                    return fs if 'Transfer-Encoding' in response.headers or (fs.size != None and int(fs.size) > 0) else None
                else:
                    encoding = response.headers.get_content_charset()
                    if not encoding: encoding = 'iso-8859-1'
                    string = response.read().decode(encoding)
                    if self.__debug: print("\n", "< Response Body:\n", string, "\n", sep="")
                    try:
                        data = json.loads(string)
                    except ValueError:  # PUT requests don't return anything
                        data = None
                    return data
                
            elif response.code == 404:
                return None
            
            else:
                encoding = response.headers.get_content_charset()
                if not encoding: encoding = 'iso-8859-1'
                string = response.read().decode(encoding)                    
                try:
                    msg = json.loads(string)['error_message']
                except ValueError:
                    msg = string
                raise ApiException(response.code, msg)
        except urllib.error.HTTPError as e:
            raise ApiException(e.code, e.msg)
                
        finally:
            if isFileUpload:
                try:
                    postData.inputStream.close()
                except Exception as e:
                    pass
            if self.__debug:
                http.client.HTTPConnection.debuglevel = 0
                if self.__logFilepath:
                    sys.stdout = stdOut
                    logFile.close()
            

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
        elif type(obj) in [str, int, float, bool]:
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
                    for (key, val) in objDict.items()
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

            if (objClass in ['int', 'float', 'dict', 'list', 'str']):
                objClass = eval(objClass)
            else:  # not a native type, must be model class
                objClass = eval(objClass + '.' + objClass)

        if objClass in [str, int, float, bool]:
            return objClass(obj)
        elif objClass == datetime:
            # Server will always return a time stamp in UTC, but with
            # trailing +0000 indicating no offset from UTC. So don't process
            # last 5 characters.
            return datetime.datetime.strptime(obj[:-5],
                                              "%Y-%m-%dT%H:%M:%S.%f")

        instance = objClass()

        for attr, attrType in instance.swaggerTypes.items():
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
                        value = str(value)
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
        encoded = urllib.parse.quote(url, safe='~@#$&()*!=:;,.?/\'').replace("%25", "%")
        return encoded

    @staticmethod
    def encodeURIComponent(url):
        return urllib.parse.quote(url, safe='~()*!.\'')

    @staticmethod
    def readAsDataURL(filePath):
        mimetype = mimetypes.guess_type(filePath, False)[0] or "application/octet-stream"
        filecontents = open(filePath, 'rb').read()
        return 'data:' + mimetype + ';base64,' + base64.b64encode(filecontents).decode()


class MethodRequest(urllib.request.Request):

    def __init__(self, *args, **kwargs):
        """Construct a MethodRequest. Usage is the same as for
        `urllib.Request` except it also takes an optional `method`
        keyword argument. If supplied, `method` will be used instead of
        the default."""

        if 'method' in kwargs:
            self.method = kwargs.pop('method')
        return urllib.request.Request.__init__(self, *args, **kwargs)

    def get_method(self):
        return getattr(self, 'method', urllib.request.Request.get_method(self))

class ApiException(Exception):
    def __init__(self, code, *args):
        super(Exception, self).__init__((code, ) + args)
        self.code = code
