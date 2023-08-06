from django.conf import settings
from django.http import HttpResponse, Http404
import base64
import json
import urllib

class VingdException(Exception):
    pass

def encode64(data):
    return base64.b64encode(json.dumps(data))
    
def decode64(data):
    padding = '===='
    data += padding[:(4-len(data))%4]
    return json.loads(base64.b64decode(data))

def append_get_params(url, dict):
    url = url.encode('utf-8')
    params = urllib.urlencode(dict)
    delimiter = '?'
    if url.find('?')!=-1:
        delimiter = '&'
    url += delimiter + params
    return url

class HttpResponseJSON(HttpResponse):
    def __init__(self, dict):
        super(HttpResponseJSON, self).__init__(json.dumps(dict), mimetype="application/json", )
