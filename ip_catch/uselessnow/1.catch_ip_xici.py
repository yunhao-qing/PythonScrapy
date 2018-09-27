# -*- coding=utf-8 -*-
import datetime
from lxml import etree
import requests



class getProxy():

    def __init__(self):
        self.user_agent = "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0)"
        self.header = {"User-Agent": self.user_agent}

    def getContent(self, num):
        nn_url = "http://www.xicidaili.com/nt/" + str(num)
        requests.get(nn_url)
        r = requests.get(nn_url, headers=self.header, timeout=500)
        r.encoding = 'utf-8'
        content = r.text
        et = etree.HTML(content)
        result_even = et.xpath('//tr[@class=""]')
        result_odd = et.xpath('//tr[@class="odd"]')

        for i in result_even:
            t1 = i.xpath("./td/text()")[:2]
            print ("IP:%s\tPort:%s" % (t1[0], t1[1]))
            #ip_list.save({'ip+port':t1[0]+":"+t1[1],'type':'http','source':'xicidaili'})

        for i in result_odd:
            t2 = i.xpath("./td/text()")[:2]
            print ("IP:%s\tPort:%s" % (t2[0], t2[1]))
            #ip_list.save({'ip+port':t2[0]+":"+t2[1],'type':'http','source':'xicidaili'})

    def loop(self,page1,page2):
        for i in range(page1,page2):
            self.getContent(i)
            print (i)

if __name__ == "__main__":
    now = datetime.datetime.now()
    print ("Start at %s" % now)
    obj=getProxy()
    obj.loop(1,10)
    #479-502 unsure whether plugged in