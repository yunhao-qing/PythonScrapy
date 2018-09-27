# -*- coding=utf-8 -*-
import requests
import datetime
from lxml import etree
import pymongo

connection=pymongo.MongoClient('192.168.1.88',27017)
db=connection.ichunt
ip_list = db.ips

class getProxy():
    def __init__(self):
        self.user_agent = "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0)"
        self.header = {"User-Agent": self.user_agent}

    def proxydb(self,num):
        nn_url = "http://proxydb.net/?offset=0"+ str(num*50)
        r = requests.get(nn_url, headers=self.header,timeout = 500)
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
            td = tr.xpath('./td')[1]
            raw_type = td.xpath('./text()')[0]
            type=raw_type.strip()
            if type=='HTTP':
                ipport="http://"+raw_ipport
            elif type=='HTTPS':
                ipport = "https://" + raw_ipport
            print(ipport)


    def loop_proxydb(self,page1,page2):
        for i in range(page1,page2):
            self.proxydb(i)
            print("proxydb")
            print (i)

if __name__ == "__main__":
    now = datetime.datetime.now()
    print ("Start at %s" % now)
    obj=getProxy()
    obj.loop_proxydb(1,174)