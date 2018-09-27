# -*- coding: utf-8 -*-
# !/usr/bin/env python
import re
import sys
import pika
import requests
from lxml import etree
import logging
import threading
import time
import pprint
from server.settings import rabbitmq_server
import json
requests.packages.urllib3.disable_warnings()

class ProxyIPSpider:
    def __init__(self, spider_result):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_3) '+\
                    'AppleWebKit/537.36 (KHTML, like Gecko)',
        }
        self.spider_result = spider_result

    def get_1(self, scan_pages):
        url_1 = "http://www.xicidaili.com/nn/%d"
        url_2 = "http://www.xicidaili.com/nt/%d"
        base_url = ''
        for i in range(2):
            if i == 0:
                base_url = url_1
            else:
                base_url = url_2
            for page in range(1, scan_pages+1):
                result = []
                try:
                    r = requests.get(base_url % page, 
                            headers=self.headers,timeout=30)
                    r.encoding = 'utf-8'
                    tree = etree.HTML(r.text)
                    odds = tree.xpath('//tr[@class="odd"]')
                    for odd in odds:
                        tds = odd.xpath('./td')
                        ip = ''.join(tds[1].xpath('./text()')).strip()
                        port = ''.join(tds[2].xpath('./text()')).strip()
                        protocol = ''.join(tds[5].xpath('./text()')).\
                                strip().lower()
                        with LOCK: 
                            self.spider_result.append( 
                                    str({protocol: protocol+'://'+ip+':'+port}))
                except Exception as e:
                    print(e)

    def get_2(self, scan_pages):
        url_1 = "http://www.nianshao.me/?stype=1&page=%d"
        url_2 = "http://www.nianshao.me/?stype=2&page=%d"
        base_url = ''
        for i in range(2):
            if i == 0:
                base_url = url_1
            else:
                base_url = url_2
            for page in range(1,scan_pages+1):
                try:
                    r = requests.get(base_url % page, headers=self.headers,
                            timeout = 30)
                    r.encoding = 'utf-8'
                    html = r.text
                    tree = etree.HTML(html)
                    table = tree.xpath('//table')
                    table = table[0] if table else None
                    tbody = table.xpath('./tbody')
                    tbody = tbody[0] if tbody else None
                    trs = tbody.xpath('./tr')
                    for tr in trs:
                        td = tr.xpath('./td')[0]
                        ip = td.xpath('./text()')[0]
                        td = tr.xpath('./td')[1]
                        port = td.xpath('./text()')[0]
                        td = tr.xpath('./td')[4]
                        protocol = td.xpath('./text()')[0].lower()
                        with LOCK: 
                            self.spider_result.append( 
                                    str({protocol: protocol+'//:'+ip+':'+port}))
                except Exception as e:
                    print(e)

    def get_3(self, scan_pages):
        url = "http://www.66ip.cn/%d.html"
        for page in range(1, scan_pages+1):
            try:
                r = requests.get(url % page, headers=self.headers,timeout=30)
                r.encoding = 'utf-8'
                html = r.text
                tree = etree.HTML(html)
                table = tree.xpath('//table')
                table = table[2] if table else None
                trs_withtitles = table.xpath('./tr')
                trs = trs_withtitles[1:]

                for tr in trs:
                    td = tr.xpath('./td')[0]
                    ip = td.xpath('./text()')[0]
                    td = tr.xpath('./td')[1]
                    port = td.xpath('./text()')[0]
                    with LOCK:
                        self.spider_result.append(str({'http': 'http://'+ip+':'+port}))
                        self.spider_result.append(str({'https': 'https://'+ip+':'+port}))
            except Exception as e:
                print(e)

    def get_4(self, scan_pages):
        urls = [
            'http://www.xsdaili.com/index.php?s=/index/mfdl/type/1/p/%d.html',
            'http://www.xsdaili.com/index.php?s=/index/mfdl/type/2/p/%d.html',
            'http://www.xsdaili.com/index.php?s=/index/mfdl/type/3/p/%d.html',
            'http://www.xsdaili.com/index.php?s=/index/mfdl/type/4/p/%d.html',
        ]

        for url in urls:
            for i in range(1, scan_pages+1):
                try:
                    r = requests.get(url, headers=self.headers, timeout=30)
                    r.encoding = 'utf-8'
                    html = r.text
                    tree = etree.HTML(html)
                    table = tree.xpath('//table[@class="table table-bordered table-striped"]')
                    table = table[0] if table else None
                    tbody = table.xpath('./tbody')
                    tbody = tbody[0] if tbody else None
                    trs = tbody.xpath('./tr')
                    for tr in trs:
                        td = tr.xpath('./td')[0]
                        ip = td.xpath('./text()')[0]
                        td = tr.xpath('./td')[1]
                        port = td.xpath('./text()')[0]
                        td = tr.xpath('./td')[3]
                        protocol = td.xpath('./text()')[0].lower()
                        with LOCK:
                            self.spider_result.append(str({protocol: protocol+'://'+ip+':'+port}))
                except Exception as e:
                    print(e)

    def get_5(self, scan_pages=1):
        url= "http://ip.yqie.com/ipproxy.htm"
        try:
            r = requests.get(url, headers=self.headers,timeout=30)
            r.encoding = 'utf-8'
            html = r.text
            tree = etree.HTML(html)
            raw_tables = tree.xpath('//table')
            tables=raw_tables[:4]
            for table in tables:
                trs = table.xpath('./tr')
                trss=trs[1:]
                for tr in trss:
                    tds = tr.xpath("./td/text()")
                    ipport = str(tds[4] + "://" + tds[0] + ":" + tds[1]).lower()
                    with LOCK:
                        self.spider_result.append(str({tds[4].lower(): ipport}))
        except Exception as e:
            print(e)

    def get_6(self, scan_pages):
        urls = [
            "http://www.iphai.com/free/ng",
            "http://www.iphai.com/free/np",
            "http://www.iphai.com/free/wg",
            "http://www.iphai.com/free/wp",
        ]
        for url in urls:
            try:
                r = requests.get(url, headers=self.headers,timeout=30)
                r.encoding = 'utf-8'
                html = r.text
                tree = etree.HTML(html)
                trs = tree.xpath('//tr')
                tr=trs[1:]
                for i in tr:
                    td = i.xpath("./td/text()")[:2]
                    ip=str(td[0]).strip()
                    port=str(td[1]).strip()
                    ipport="http://"+ip+":"+port
                    with LOCK:
                        self.spider_result.append(str({'http': ipport}))
            except Exception as e:
                print(e)

    '''
    def get_8(self, scan_pages=1):
        url = "http://proxydb.net/?protocol=%s&offset=1"
        for protocol in ['http', 'https']:
            try:
                r = requests.get(url % protocol, headers=self.headers,timeout=50)
                r.encoding = 'utf-8'
                html = r.text
                tree = etree.HTML(html)
                table = tree.xpath('//table[@class="table table-sm"]')
                table = table[0] if table else None
                tbody = table.xpath('./tbody')
                tbody = tbody[0] if tbody else None

                trs = tbody.xpath('./tr')
                for tr in trs:
                    td = tr.xpath('./td')[0]
                    raw_ipport = td.xpath('./a')[0].xpath('./text()')[0]
                    ipport=protocol+'://'+raw_ipport
                    with LOCK:
                        self.spider_result.append( {protocol: ipport})
            except Exception as e:
                print(e)
    '''


    def get_7(self, scan_pages):
        url = "http://www.dlip.cn/gng/index_%d.html"
        for page in range(scan_pages+1):
            try:
                r = requests.get(url%page, headers=self.headers, timeout=30)
                r.encoding = 'utf-8'
                content = r.text
                et = etree.HTML(content)
                result = et.xpath('//tr')
                for i in result:
                    try:
                        t = i.xpath("./td/text()")[:2]
                        ipport = str("http://" + t[0] + ":" + t[1])
                        with LOCK:
                            self.spider_result.append(str({'http':ipport}))
                    except:
                        pass
            except Exception as e:
                print(e)

LOCK = threading.Lock()

TASK_COMPLETE = []

def next(pis, get_n):
    eval('pis.%s(3)' % get_n)
    print(get_n, '已采集完毕')
    with LOCK:
        TASK_COMPLETE.append(get_n)

def start_spider():
    spider_result = []
    pis = ProxyIPSpider(spider_result)
    ps_methods = [x  for x in dir(pis) if x.startswith('get')]    
    print(ps_methods)

    for m in ps_methods:
        threading.Thread(target=next, args=(pis, m)).start()

    while threading.activeCount() >= 2:
        print('正在采集代理IP请稍后, 还剩下%d线程' % threading.activeCount())
        time.sleep(2)

    print('代理IP采集完毕, 下面打印出前10个, 所有的采集结果都包含在spider_result中',
            '总共采集%d个' % len(spider_result))
    print('这些采集任务已归队', TASK_COMPLETE)
    pprint.pprint(spider_result[:10])

    return spider_result

def check_proxy(proxy, crs, url, keyword):
    '''
    url = http://digikey.cn, https://verical.com
    '''
    print('正在用%s访问%s' % (str(proxy), url))
    global LOCK
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_3) '+\
                'AppleWebKit/537.36 (KHTML, like Gecko)',
    }

    is_ok = True
    try:
        r = requests.get(url, timeout=30, headers=headers, proxies=proxy,
                verify=False)
        r.encoding = 'utf-8'
        if r.status_code == 200:
            if '无效用户' in r.text:
                print('无效用户')
                is_ok = False
            if keyword not in r.text:
                print(keyword, '不在返回的html中')
                is_ok = False
        else:
            is_ok = False
    except Exception as e:
        print(e)
        is_ok = False

    if is_ok:
        with LOCK:
            crs.append(proxy)

def init_mongo():
    '''
    初始化mongo1, 抓取代理放入mongo1
    '''
    sr = start_spider()
    sr = ['{"proxy":"%s"}' % i for i in sr if '\r\n' not in i]
    
    from server.db.proxy_ip.mongo_client import ProxyIPTmp
    proxies = ProxyIPTmp.get_all_proxies()
    proxies = ['{"proxy":"%s"}' % i for i in proxies]
    result = set(proxies + sr)
    rs = [] 
    for r in result:
        try:
            tmp = eval(r)
            if 'proxy' not in tmp:
                continue
            rs.append(tmp)
        except:
            pass
    import pprint
    pprint.pprint(rs)
    ProxyIPTmp.removeall()
    ProxyIPTmp.addProxyIPTmp(rs)

def check_update(proxy_queue, url, keyword):
    '''
    使用url检查mongo1中的数据放入proxy_queue队列
    '''
    from server.db.proxy_ip.mongo_client import ProxyIPTmp
    print('当前的线程数', threading.activeCount())
    proxies = ProxyIPTmp.get_all_proxies()
    result = proxies
    i = 0
    crs = []
    ts = []
    while i < len(result):
        if threading.activeCount() <= 200:
            try:
                t = threading.Thread(target=check_proxy, 
                        args=(eval(result[i]),crs, url, keyword))
                ts.append(t)
                t.start()
            except:
                pass
            i += 1
        else:
            print('正在检测mongo里的ip', i)
            print('可用代理', crs)
            time.sleep(1)
    for t in ts:
        t.join()

    print('线程结束')
    print('检测完毕')
    import pprint
    crs = [str(i) for i in crs]
    pprint.pprint(crs)
    for cr in crs:
        push_to_proxy_ip(proxy_queue, cr)

def push_to_proxy_ip(proxy_queue, proxies):
    from server.send_cron.verical.send_goods import get_rb_conn
    conn = get_rb_conn()
    ch = conn.channel()
    ch.queue_declare(queue=proxy_queue, durable=True)
    print('正在推送', proxies, '到队列%s' % proxy_queue)
    ch.basic_publish(exchange='', routing_key=proxy_queue,
                properties=pika.BasicProperties(
                    delivery_mode=2,  # make message persistent
                ),
                body=proxies)
    conn.close()

if __name__ == '__main__':
    #init_mongo()
    #check_update('proxy_ip_digikey', 'http://digikey.cn', 'digikey')
    check_update('proxy_ip_verical', 'https://verical.com', 'verical')
