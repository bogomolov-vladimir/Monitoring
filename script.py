import os
#import sys
import requests
import base64
import hmac
import hashlib
import binascii
#import pandas as pd
import json
import time
from prometheus_client import start_http_server, Summary, Gauge

markets_url = os.environ.get('ISUN_MARKETS_URL', "")
sid = os.environ.get('ISUN_SID', '')
key = os.environ.get('ISUN_KEY', '')
secret = os.environ.get('ISUN_SECRET', '')
url = markets_url
path='/api/v1/wallet/list'
Cur_list=[]
#title_table=pd.DataFrame(['AVAILABLE','RESERVED','TOTAL','ORIGIN'], columns=['Title'])


def hmac_value(key,data):
    #return "3d1cadcfd259dd686e4a817bc70025c7084da26971a84a2ca3c3a05eac23c74e"
    byte_key = bytes(key, 'UTF-8')
    #byte_key = binascii.unhexlify(key)
    h = hmac.new(byte_key, data.encode(), hashlib.sha256)
    return h.hexdigest()


def getjson_private(path,sid,key,secret,url,extra_params={}):
    headers = {"X-api-sid": sid,
        "X-api-key": key,
        "X-api-key-checksum": hmac_value(secret,path+":"),
        "Content-Type": "application/json"}
    params = {}
    for e in extra_params:
        params[e] = extra_params[e]
    response = requests.get(url+path,params = params,headers=headers)
    if response.status_code == 200:
        if (len(response.json())==0):return None
        return response.json()
    else:return response.json()
    raise Exception ("Invalid status code "+str(response.status_code)+" url:"+url+" message"+str(response.content))

gA = Gauge('isAvailable', 'Currency Available', labelnames=['currency'])
gR = Gauge('reserved', 'Currency Reserved', labelnames=['currency'])

if __name__ == '__main__':
    # Start up the server to expose the metrics.
    start_http_server(8887)
    # Generate some requests.
    while True:
        pre_data=getjson_private(path,sid,key,secret,url)
        gRvalues = [[i['currencyCode'],i['reserved']] for i in pre_data['list']]
        gAvalues = [[i['currencyCode'],i['isAvailable']] for i in pre_data['list']]
        for C,V in gAvalues:
            print(C, V)
            gA.labels(C).set(V)
        for C,V in gRvalues:
            gR.labels(C).set(V)
        time.sleep(10)
