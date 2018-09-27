# -*- coding=utf-8 -*-
import urllib.request
import urllib.parse
import datetime
from lxml import etree
import pymongo

connection=pymongo.MongoClient('192.168.1.88',27017)
db=connection.ichunt
ip_list = db.ips


class getProxy_dlip_gnp():

    def __init__(self):
        self.user_agent = "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0)"
        self.header = {"User-Agent": self.user_agent}

    def getContent(self, num):
        nn_url = "http://www.dlip.cn/gnp/index_"+str(num)+".html"
        req = urllib.request.Request(nn_url, headers=self.header)
        resp = urllib.request.urlopen(req)
        content = resp.read()
        tree = etree.HTML(content)
        table = tree.xpath('//table[@id="ip_list"]')
        table = table[0] if table else None
        trs = table.xpath('./tr')
        for tr in trs:
            td = tr.xpath('./td')[0]
            print(td)
            #ip_list.save({'ip+port': ipport, 'type': type,'source':"proxydb"})
            print (i)

    def loop(self, page1, page2):
        for i in range(page1, page2):
            self.getContent(i)
            print(i)


class getProxy_dlip_gng():

    def __init__(self):
        self.user_agent = "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0)"
        self.header = {"User-Agent": self.user_agent}

    def getContent(self, num):
        nn_url = "http://www.dlip.cn/gnp/index_"+str(num)+".html"
        req = urllib.request.Request(nn_url, headers=self.header)
        resp = urllib.request.urlopen(req)
        content = resp.read()
        et = etree.HTML(content)
        result_even = et.xpath('//tr[@class=""]')
        result_odd = et.xpath('//tr[@class="odd"]')

        for i in result_even:
            t1 = i.xpath("./td/text()")[:2]
            print ("IP:%s\tPort:%s" % (t1[0], t1[1]))
            #ip_list.save({'ip':t1[0], 'port':t1[1],'type':'http'})

        for i in result_odd:
            t2 = i.xpath("./td/text()")[:2]
            print ("IP:%s\tPort:%s" % (t2[0], t2[1]))
            #ip_list.save({'ip':t2[0], 'port':t2[1],'type':'http'})

    def loop(self,page1,page2):
        for i in range(page1,page2):
            self.getContent(i)
            print (i)

if __name__ == "__main__":
    now = datetime.datetime.now()
    print ("Start at %s" % now)
    obj=getProxy_dlip_gnp()
    obj.loop(2,57)
    #obj_2=getProxy_dlip_gng
    #obj_2.loop(3,201)