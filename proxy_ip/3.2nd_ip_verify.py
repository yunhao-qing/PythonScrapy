# -*- coding=utf-8 -*-
import pika
import time
import socket
import requests
import datetime
from threading import active_count,Thread, Lock
import threading
from settings import rabbitmq_server
from db import ProxyIP,get_mongo_con
lock = Lock()

HTTP_PROXY_IP = 'http_proxy_ip'

db=get_mongo_con()
ip_checked_list=db.ips_checked

def init():
    global HTTP_PROXY_IP
    host = rabbitmq_server['host']
    user = rabbitmq_server['user']
    password = rabbitmq_server['password']
    credentials = pika.PlainCredentials(user, password)
    connection = pika.BlockingConnection(pika.ConnectionParameters(
            host=host, credentials=credentials))
    channel = connection.channel()
    channel.queue_declare(queue=HTTP_PROXY_IP, durable=True)
    return channel

def test(i, ch, new_ips):
    global HTTP_PROXY_IP, lock
    user_agent = "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0)"
    header = {"User-Agent": user_agent}
    sock = socket.socket()
    sock.settimeout(5)
    pi = {'http': new_ips[i]}
    url = "http://www.baidu.com"
    try:
        starttime = datetime.datetime.now()
        r = requests.get(url, headers=header, timeout=20,
                         proxies=pi)
        endtime = datetime.datetime.now()
        if r.status_code == 200:
            with lock:
                print(new_ips[i], 'is OK','time_used:',endtime-starttime)
                pi = {'http': new_ips[i]}
                body = str(pi)
                ch.basic_publish(exchange='',
                                 routing_key=HTTP_PROXY_IP,
                                 body=body,
                                 properties=pika.BasicProperties(
                                     delivery_mode=2,  # make message persistent
                                 ),
                                 )
        else:
            pass
    except Exception as e:
        pass
    finally:
        sock.close()

if __name__ == "__main__":
    channel = init()
    new_ips = ProxyIP.get_all_checkedIPs()
    i = 1
    while i < len(new_ips):
        if active_count() <= 200:
            Thread(target=test, args=(i,channel, new_ips)).start()
            i += 1
        else:
            print('[当前扫描的端口上限 %d]' % i)
            time.sleep(5)
    while active_count() > 5:
        print('等待所有线程结束')
        print(threading.enumerate())
        time.sleep(5)

