# -*- coding=utf-8 -*-
import datetime
from lxml import etree
import requests

class getProxy():

    def __init__(self):
        self.user_agent = "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0)"
        self.header = {"User-Agent": self.user_agent}

    def dlip(self, num):
        nn_url = "http://www.dlip.cn/gng/index_"+str(num)+".html"
        requests.get(nn_url)
        r = requests.get(nn_url, headers=self.header, timeout=500)
        r.encoding = 'utf-8'
        content = r.text
        et = etree.HTML(content)
        result = et.xpath('//tr')
        for i in result:
            try:
                t1 = i.xpath("./td/text()")[:2]
                print ("IP:%s\tPort:%s" % (t1[0], t1[1]))
                #ip_list.save({'ip+port':t1[0]+":"+t1[1],'type':'http','source':'xicidaili'})
            except:
                pass


    def loop_dlip(self,page1,page2):
        for i in range(page1,page2):
            self.dlip(i)
            print (i)

if __name__ == "__main__":
    now = datetime.datetime.now()
    print ("Start at %s" % now)
    obj=getProxy()
    obj.loop(2,10)
    #479-502 unsure whether plugged in