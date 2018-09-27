# -*- coding=utf-8 -*-
import requests
import datetime
from lxml import etree
import pymongo

connection=pymongo.MongoClient('192.168.1.88',27017)
db=connection.ichunt
ip_list = db.ips

class getProxy_ip3366():
    def __init__(self):
        self.user_agent = "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0)"
        self.header = {"User-Agent": self.user_agent}

    def getContent(self,num):
        count=0
        nn_url = "http://www.ip3366.net/?stype=1&page="+ str(num)
        r = requests.get(nn_url, headers=self.header)
        r.encoding = 'utf-8'
        html = r.text
        et = etree.HTML(html)
        all = et.xpath('//tr')
        result=all[1:]

        for i in result:
            t = i.xpath("./td/text()")[:4]
            print ("IP:%s\tPort:%s\tType:%s" % (t[0], t[1],t[3]))
            count = count+1

        print(count)


    def loop_ip3366(self,page1,page2):
        for i in range(page1,page2):
            self.getContent(i)
            print (i)

if __name__ == "__main__":
    now = datetime.datetime.now()
    print ("Start at %s" % now)
    obj=getProxy_ip3366()
    obj.loop_ip3366(1,11)