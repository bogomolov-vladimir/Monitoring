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

markets_url = os.environ.get('ISUN_MARKETS_URL', "https://pub-new.unitex.one")
sid = os.environ.get('ISUN_SID', '628a9ed9-100d-429d-8baa-3771f747612a')
key = os.environ.get('ISUN_KEY', '2d8fd882-5dc5-4451-8422-52736e90ac84')
secret = os.environ.get('ISUN_SECRET', '6c86b656a8c23dded9f474a69e29a91f3ad0574a2f6fc3567162cd5df164c7a7')
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
