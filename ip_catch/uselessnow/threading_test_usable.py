# -*- coding=utf-8 -*-
import urllib.request
import pymongo
import threading
import socket

connection=pymongo.MongoClient('192.168.1.88',27017)
db=connection.ichunt
ip_list = db.ips

proxys = []
for data in ip_list.find():
    a=data['ip+port']
    proxy_temp = {"http": "http://" + str(a)}
    proxys.append(proxy_temp)

proxy_ip = open('proxy_ip.txt', 'w')  # 新建一个储存有效IP的文档
lock = threading.Lock()  # 建立一个锁


def test(i):
    socket.setdefaulttimeout(5)  #设置全局超时时间
    url = "http://www.baidu.com"  #打算爬取的网址
    try:
        proxy_support = urllib.request.ProxyHandler(proxys[i])
        opener = urllib.request.build_opener(proxy_support)
        opener.addheaders=[("User-Agent","Mozilla/5.0 (Windows NT 10.0; WOW64)")]
        urllib.request.install_opener(opener)
        res = urllib.request.urlopen(url).read()
        lock.acquire()     #获得锁
        print(proxys[i],'is OK')
        #proxy_ip.write('%s\n' %str(proxys[i]))  #写入该代理IP
        lock.release()     #释放锁
    except Exception as e:
        lock.acquire()
        print(proxys[i],e)
        lock.release()

"""def test(a):
    try:
        requests.get('https://www.baidu.com/', proxies={"http": "http://" + str(a)})
        lock.acquire()  # 获得锁
        print(proxys[i], 'is OK')
        proxy_ip.write('%s\n' % str(proxys[i]))  # 写入该代理IP
        lock.release()  # 释放锁
    except Exception as e:
        lock.acquire()
        print(proxys[i], e)
        lock.release()"""


threads = []
for i in range(len(proxys)):
    thread = threading.Thread(target=test, args=[i])
    threads.append(thread)
    thread.start()
# 阻塞主进程，等待所有子线程结束
for thread in threads:
    thread.join()

proxy_ip.close()  # 关闭文件