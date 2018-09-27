# -*- coding=utf-8 -*-
import urllib.request
import pymongo
import pika
import urllib
import time
import socket
import threading
from threading import active_count,Thread, Lock
lock = Lock()

HTTP_PROXY_IP = 'http_proxy_ip'

rabbitmq_server = {
    'host':  '192.168.1.88',
    'user':  'admin',
    'password': '123456'
}

# 0.连接数据库
connection = pymongo.MongoClient('192.168.1.88', 27017)
db = connection.ichunt
ip_list=db.ips

def init():
    global HTTP_PROXY_IP
    host = rabbitmq_server['host']
    user = rabbitmq_server['user']
    password = rabbitmq_server['password']
    credentials = pika.PlainCredentials(user, password)
    connection = pika.BlockingConnection(pika.ConnectionParameters(
            host=host, credentials=credentials))
    channel = connection.channel()
    channel.queue_declare(queue=HTTP_PROXY_IP)
    return channel

def test(i, ch, new_ips):
    global HTTP_PROXY_IP, lock
    socket.setdefaulttimeout(5)  #设置全局超时时间
    url = "http://www.baidu.com"  #打算爬取的网址
    try:
        proxy_support = urllib.request.ProxyHandler({"http": new_ips[i]})
        opener = urllib.request.build_opener(proxy_support)
        opener.addheaders=[("User-Agent","Mozilla/5.0 (Windows NT 10.0; WOW64)")]
        urllib.request.install_opener(opener)
        res = urllib.request.urlopen(url).read()
        with lock:
            print(new_ips[i],'is OK')
            pi = {'http':new_ips[i]}
            body = str(pi)
            ch.basic_publish(exchange='',
                                  routing_key=HTTP_PROXY_IP,
                                  body=body)
    except Exception as e:
        pass

if __name__ == "__main__":
    channel = init()
    new_ips = []
    for item in ip_list.find():
        new_ips.append(item['ip'])
    lock = threading.Lock()
    i = 1
    while i < len(new_ips):
        if active_count() <= 200:
            Thread(target=test, args=(i,channel, new_ips)).start()
            i += 1
        else:
            print('[当前扫描的端口上限 %d]' % i)
            time.sleep(2)

    while active_count() >= 2:
        print('等待所有线程结束')

    print("zzz done")

