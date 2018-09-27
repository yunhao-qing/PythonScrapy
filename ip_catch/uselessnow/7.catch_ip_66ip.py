# -*- coding=utf-8 -*-
import requests
import datetime
from lxml import etree
import pymongo

connection=pymongo.MongoClient('192.168.1.88',27017)
db=connection.ichunt
ip_list = db.ips3_66ip

class getProxy():
    def __init__(self):
        self.user_agent = "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0)"
        self.header = {"User-Agent": self.user_agent}

    def ip66(self,num):
        nn_url = "http://www.66ip.cn/"+ str(num)+".html"
        r = requests.get(nn_url, headers=self.header)
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
            print("http"+"://"+ip+":"+port)
            #ip_list.save({'ip': ip, 'port': port})

    def loop_ip66(self,page1,page2):
        for i in range(page1,page2):
            self.getContent(i)
            print (i)

if __name__ == "__main__":
    now = datetime.datetime.now()
    print ("Start at %s" % now)
    obj=getProxy()
    obj.ip66(1,201)
