# -*- coding=utf-8 -*-
import pymongo
import requests

connection=pymongo.MongoClient('192.168.1.88',27017)
db=connection.ichunt
ip_list = db.ips

def validateIp(ipport):
    try:
        requests.get('http://baidu.com', proxies={"http": "http://"+ipport})
    except:
        print('connect failed')
    else:
        print('success')

for data in ip_list.find():
    a=str(data['ip+port'])
    validateIp(a)
    print("what")

