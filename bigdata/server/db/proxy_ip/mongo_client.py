from server.db import connection_pool
from datetime import datetime
import time

PROXY_IP_CONN = connection_pool.get_mongo_conn_no_auth('mongo_proxy_ip')

class ProxyIPTmp(dict):
    @classmethod
    def addProxyIPTmp(cls, proxies):
        PROXY_IP_CONN.proxy_ip_tmp.insert_many(proxies)

    @classmethod
    def removeall(cls):
        PROXY_IP_CONN.proxy_ip_tmp.remove()

    @classmethod
    def get_all_proxies(cls):
        code = 'PROXY_IP_CONN.proxy_ip_tmp.find()'
        proxies = eval(code)
        res = []
        for p in proxies:
            print(p)
            res.append(p['proxy'])
        return res

class ProxyIP(dict):
    @classmethod
    def addProxyIP(cls, proxies):
        PROXY_IP_CONN.proxy_ip.insert_many(proxies)

    @classmethod
    def removeall(cls):
        PROXY_IP_CONN.proxy_ip.remove()

    @classmethod
    def get_all_proxies(cls):
        code = 'PROXY_IP_CONN.proxy_ip.find()'
        proxies = eval(code)
        res = []
        for p in proxies:
            res.append(p['proxy'])
        return res
