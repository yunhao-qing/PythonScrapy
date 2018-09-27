# -*- coding=utf-8 -*-
import requests
import datetime
from lxml import etree
import pymongo

connection=pymongo.MongoClient('192.168.1.88',27017)
db=connection.ichunt
ip_list = db.ips

class getProxy_ip181():
    def __init__(self):
        self.user_agent = "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0)"
        self.header = {"User-Agent": self.user_agent}

    def getContent(self,num):
        count=0
        nn_url = "http://www.ip181.com/daili/"+ str(num) +".html"
        r = requests.get(nn_url, headers=self.header)
        r.encoding = 'utf-8'
        html = r.text
        et = etree.HTML(html)
        all = et.xpath('//tr')
        result=all[1:]

        for i in result:
            t = i.xpath("./td/text()")[:4]
            print ("IP:%s\tPort:%s\tType:%s" % (t[0], t[1],t[3]))
            ip_list.save({'ip+port':t[0]+":"+t[1], 'type':t[3],'source':"ip181"})
            count = count+1

        print(count)


    def loop(self,page1,page2):
        for i in range(page1,page2):
            self.getContent(i)
            print (i)

if __name__ == "__main__":
    now = datetime.datetime.now()
    print ("Start at %s" % now)
    obj=getProxy_ip181()
    obj.loop(1,881)