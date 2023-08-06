#Verion 1.0
#Author wendal(wendal1985@gmail.com)
#If you find a bug, pls mail me

import sys
import httplib

ERROR = 'HTTPSQS_ERROR'

GET_END = 'HTTPSQS_GET_END'

PUT_OK = 'HTTPSQS_PUT_OK'
PUT_ERROR = 'HTTPSQS_PUT_ERROR'
PUT_END = 'HTTPSQS_PUT_END'

RESET_OK = 'HTTPSQS_RESET_OK'
RESET_ERROR = 'HTTPSQS_RESET_ERROR'

MAXQUEUE_OK = 'HTTPSQS_MAXQUEUE_OK'
MAXQUEUE_CANCEL = 'HTTPSQS_MAXQUEUE_CANCEL'

SYNCTIME_OK = 'HTTPSQS_SYNCTIME_OK'
SYNCTIME_CANCEL = 'HTTPSQS_SYNCTIME_CANCEL'

class Httpsqs(object):
    def __init__(self,host,port=1218):
        self.host = host
        self.port = port
    
    def get(self,poolName):
        conn = httplib.HTTPConnection(self.host,self.port)
        conn.request("GET", "/?opt=get&name=" + poolName)
        r = conn.getresponse()
        if r.status == httplib.OK :
            data = r.read()
            conn.close()
            return data
        return ''

    def put(self,poolName,data):
        conn = httplib.HTTPConnection(self.host,self.port)
        conn.request("POST", "/?opt=put&name="+poolName,data)
        r = conn.getresponse()
        if r.status == httplib.OK :
            data = r.read()
            return data
        return ''

    def status(self,poolName):
        conn = httplib.HTTPConnection(self.host,self.port)
        conn.request("GET", "/?opt=status&name="+poolName)
        r = conn.getresponse()
        if r.status == httplib.OK :
            data = r.read()
            return data
        return ''
    
    def status_json(self,poolName):
        conn = httplib.HTTPConnection(self.host,self.port)
        conn.request("GET", "/?opt=status_json&name="+poolName)
        r = conn.getresponse()
        if r.status == httplib.OK :
            data = r.read()
            return data
        return ''

    def reset(self,poolName):
        conn = httplib.HTTPConnection(self.host,self.port)
        conn.request("GET", "/?opt=reset&name="+poolName)
        r = conn.getresponse()
        if r.status == httplib.OK :
            data = r.read()
            return data
        return ''

    def maxlen(self,poolName,num):
        conn = httplib.HTTPConnection(self.host,self.port)
        conn.request("GET", "/?opt=maxqueue&name="+poolName+"&num="+str(num))
        r = conn.getresponse()
        if r.status == httplib.OK :
            data = r.read()
            return data
        return ''

    def synctime(self,poolName,num):
        conn = httplib.HTTPConnection(self.host,self.port)
        conn.request("GET", "/?opt=synctime&name="+poolName+"&num="+str(num))
        r = conn.getresponse()
        if r.status == httplib.OK :
            data = r.read()
            return data
        return ''

def isOK(data):
    if data is '' :
        return False
    if data is ERROR :
        return False
    if data is GET_END :
        return False
    if data is PUT_ERROR :
        return False
    if data is RESET_ERROR :
        return False
    if data is MAXQUEUE_CANCEL :
        return False
    if data is SYNCTIME_CANCEL :
        return False
    return True
    
