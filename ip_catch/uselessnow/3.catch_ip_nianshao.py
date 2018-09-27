# -*- coding=utf-8 -*-
import requests
import datetime
from lxml import etree
import pymongo

connection=pymongo.MongoClient('192.168.1.88',27017)
db=connection.ichunt
ip_list = db.ips

class getProxy_nianshao():
    def __init__(self):
        self.user_agent = "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0)"
        self.header = {"User-Agent": self.user_agent}

    def nianshao(self,num):
        urls=["",""]
        urls[0] = "http://www.nianshao.me/?stype=1&page="+str(num)
        urls[1] = "http://www.nianshao.me/?stype=2&page=" + str(num)
        for url in urls:
            r = requests.get(url, headers=self.header)
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
                type = td.xpath('./text()')[0]
                print(type+"://"+ip+":"+port)

    def loop_nianshao(self, page1, page2):
        for i in range(page1, page2):
            self.nianshao(i)
            print(i)


if __name__ == "__main__":
    now = datetime.datetime.now()
    print ("Start at %s" % now)
    obj.loop(1,101)
