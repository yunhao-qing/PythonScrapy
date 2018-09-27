# -*- coding=utf-8 -*-
import requests
import datetime
from lxml import etree
import pymongo

connection=pymongo.MongoClient('192.168.1.88',27017)
db=connection.ichunt
ip_list = db.ips5_ipyqle

class getProxy():
    def __init__(self):
        self.user_agent = "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0)"
        self.header = {"User-Agent": self.user_agent}

    def ipyqle(self):
        nn_url = "http://ip.yqie.com/ipproxy.htm"
        r = requests.get(nn_url, headers=self.header)
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
                print(ipport)


if __name__ == "__main__":
    now = datetime.datetime.now()
    print ("Start at %s" % now)
    obj=getProxy()
    obj.getContent()
