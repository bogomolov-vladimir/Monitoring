#!/bin/bash
import os
import requests
import base64
import hmac
import hashlib
import binascii
import json
import time
from prometheus_client import start_http_server, Summary, Gauge

url = os.environ.get('ISUN_MARKETS_URL', "")
sid = os.environ.get('ISUN_SID', '')
key = os.environ.get('ISUN_KEY', '')
secret = os.environ.get('ISUN_SECRET', '')

sid2 = os.environ.get('ISUN_SID', '')
key2 = os.environ.get('ISUN_KEY', '')
secret2 = os.environ.get('ISUN_SECRET', '')

sid3=os.environ.get('ISUN_SID', '')
key3=os.environ.get('ISUN_KEY', '')
secret3=os.environ.get('ISUN_SECRET', '')

path='/api/v1/wallet/list'

def hmac_value(key,data):
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

def gauge_Preparations(param1, param2,):
    return Gauge(param1, param2, labelnames=['currency'])

gaugeAvailableTech13 = gauge_Preparations('isAvailable13', 'Currency Available13')
gaugeReservedTech13 = gauge_Preparations('reserved13', 'Currency Reserved13')
gaugeTotalTech13 = gauge_Preparations('Total13', 'Currency Total13')

gaugeAvailableTech4 = gauge_Preparations('isAvailable4', 'Currency Available4')
gaugeReservedTech4 = gauge_Preparations('reserved4', 'Currency Reserved4')
gaugeTotalTech4 = gauge_Preparations('Total4', 'Currency Total4')

gaugeAvailableTech1 = gauge_Preparations('isAvailable1', 'Currency Available1')
gaugeReservedTech1 = gauge_Preparations('reserved1', 'Currency Reserved1')
gaugeTotalTech1 = gauge_Preparations('Total1', 'Currency Total1')

if __name__ == '__main__':
    # Start up the server to expose the metrics.
    start_http_server(8889)
    # Generate some requests.
    while True:
        tech13=getjson_private(path,sid,key,secret,url)
        tech4=getjson_private(path,sid2,key2,secret2,url)
        tech1=getjson_private(path,sid3,key3,secret3,url)
        
        def gause_Parsing(gauge1,gauge2,gauge3,data):
            for item in data['list']:
                gauge1.labels(item['currencyCode']).set(item['isAvailable'])
                gauge2.labels(item['currencyCode']).set(item['reserved'])
                gauge3.labels(item['currencyCode']).set(item['isAvailable']+item['reserved'])
                print(item['currencyCode'], item['isAvailable'], item['reserved'], item['isAvailable']+item['reserved'])             
        gause_Parsing(gaugeAvailableTech13,gaugeReservedTech13,gaugeTotalTech13,tech13)
        gause_Parsing(gaugeAvailableTech4,gaugeReservedTech4,gaugeTotalTech4,tech4)
        gause_Parsing(gaugeAvailableTech1,gaugeReservedTech1,gaugeTotalTech1,tech1)
        time.sleep(10)
