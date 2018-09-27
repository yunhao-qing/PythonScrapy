from client.settings import rabbitmq_server
import pika
import time
import requests
import threading
import traceback
import sys

lock = threading.Lock()

class Spider:
    PROXY_IP = ''
    PROXY_IP_USE_COUNT = 0
    LOCAL_IP_USE_COUNT = 0

    LOCAL_START_TIME = 0
    LOCAL_NOW_TIME = 0

    PROXY_START_TIME = 0
    PROXY_END_TIME = 0

    def __init__(self):
        pass

    def http_proxies(self, CH, proxy_queue):
        print('获取HTTP代理IP')
        proxies = {}

        try:
            CH.queue_declare(queue=proxy_queue, durable=True)
            method_frame, header_frame, body = CH.basic_get(queue=proxy_queue, 
                    no_ack=True)
            if method_frame:
                print(method_frame, header_frame, body)
                body = eval(body)
                print(body)
                proxies = body
            else:
                print('No message returned')
        except Exception as e:
            print(e)
        return proxies

    def push_http_proxy_ip(self,proxies, CH, proxy_queue):
        print('推送代理IP', proxies)
        global HTTP_PROXY_IP
        CH.queue_declare(queue=proxy_queue, durable=True)
        CH.basic_publish(exchange='', routing_key=proxy_queue, 
                properties=pika.BasicProperties(
                        delivery_mode = 2),
                body=str(proxies))

    def get_no_proxies(self, url, headers, timeout):
        global lock
        if Spider.LOCAL_START_TIME == 0:
            with lock:
                Spider.LOCAL_START_TIME = time.time()
        with lock:
            Spider.LOCAL_NOW_TIME = time.time()
        mini = (Spider.LOCAL_NOW_TIME - Spider.LOCAL_START_TIME) / 60
        print('已经使用本地IP跑了%d分钟' % mini)
        try:
            r = requests.get(url, headers=headers, timeout=timeout)
            print('目标网站返回的状态码:', r.status_code)
            if r.status_code == 200:
                r.encoding = 'utf-8'
                return r.text
            return None
        except Exception as e:
            print(e)
            ex = traceback.format_exc()
            print(ex)
            return None

    def get_use_proxies(self, url, headers, timeout, ch, proxy_queue):
        global lock
        if Spider.PROXY_START_TIME == 0:
            with lock:
                Spider.PROXY_START_TIME = time.time()
        with lock:
            Spider.PROXY_END_TIME = time.time()
            Spider.PROXY_IP_USE_COUNT += 1
        mini = (Spider.PROXY_END_TIME - Spider.PROXY_START_TIME) / 60
        print('已经使用代理IP跑了%d分钟' % mini)
        try:
            if Spider.PROXY_IP in ['', {}] :
                Spider.PROXY_IP = self.http_proxies(ch, proxy_queue)
            if Spider.PROXY_IP_USE_COUNT >= 50:
                Spider.PROXY_IP = self.http_proxies(ch, proxy_queue)
                Spider.PROXY_IP_USE_COUNT = 0
            r = requests.get(url, headers=headers, timeout=timeout, 
                    proxies=Spider.PROXY_IP)
            print('目标网站返回的状态码:', r.status_code)
            if r.status_code == 200:
                r.encoding = 'utf-8'
                return r.text

            Spider.PROXY_IP = self.http_proxies(ch, proxy_queue)
            return None
        except Exception as e:
            print(e)
            Spider.PROXY_IP = self.http_proxies(ch, proxy_queue)
            ex = traceback.format_exc()
            print(ex)
            return None
