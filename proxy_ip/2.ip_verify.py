# -*- coding=utf-8 -*-
import requests
import threading
import time
import socket
from threading import active_count,Thread, Lock
from db import ProxyIP,get_mongo_con
lock = Lock()

db=get_mongo_con()
ip_list=db.ips
ip_checked_list=db.ips_checked

def test(i, new_ips, ip_checked_list):
    global lock
    user_agent = "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0)"
    header = {"User-Agent": user_agent}
    sock = socket.socket()
    sock.settimeout(5)
    pi = {'http': new_ips[i]}
    url = "http://www.baidu.com"
    try:
        r = requests.get(url, headers=header, timeout=20,
                         proxies=pi)
        if r.status_code == 200:
            with lock:
                print(new_ips[i], 'is OK')
                ip_checked_list.save({'ip': new_ips[i]})
        else:
            pass
    except Exception as e:
        pass
    finally:
        sock.close()

if __name__ == "__main__":
    raw_ips = ProxyIP.get_all_prxoyIPs()
    for item in ip_checked_list.find():
        raw_ips.append(item['ip'])
    new_ips = list(set(raw_ips))
    db.ips_checked.remove()
    i = 1
    while i < len(new_ips):
        if active_count() <= 200:
            Thread(target=test, args=(i, new_ips,ip_checked_list)).start()
            i += 1
        else:
            print('[当前扫描的端口上限 %d]' % i)
            time.sleep(5)
    while active_count() > 5:
        print('等待所有线程结束')
        print(threading.enumerate())
        time.sleep(5)
