# -*- coding=utf-8 -*-
import requests
import datetime
from lxml import etree
import pymongo

connection=pymongo.MongoClient('192.168.1.88',27017)
db=connection.ichunt
ip_list = db.ips4_xsdaili

class getProxy():
    def __init__(self):
        self.user_agent = "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0)"
        self.header = {"User-Agent": self.user_agent}

    def iphai(self, num):
        urls = ["", "", "", ""]
        urls[0] = "http://www.xsdaili.com/index.php?s=/index/mfdl/type/1/p/" + str(num) + ".html"
        urls[1] = "http://www.xsdaili.com/index.php?s=/index/mfdl/type/2/p/" + str(num) + ".html"
        urls[2] = "http://www.xsdaili.com/index.php?s=/index/mfdl/type/3/p/" + str(num) + ".html"
        urls[3] = "http://www.xsdaili.com/index.php?s=/index/mfdl/type/4/p/" + str(num) + ".html"
        for url in urls:
            r = requests.get(url, headers=self.header)
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
                type = td.xpath('./text()')[0]
                ip_list.save({'ip':ip,'type': type,'port':port})


if __name__ == "__main__":
    now = datetime.datetime.now()
    print ("Start at %s" % now)
    obj=getProxy()
    obj.