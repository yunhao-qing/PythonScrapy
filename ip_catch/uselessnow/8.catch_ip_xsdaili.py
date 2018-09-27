# -*- coding=utf-8 -*-
import requests
import datetime
from lxml import etree
import pymongo



class getProxy():
    def __init__(self):
        self.user_agent = "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0)"
        self.header = {"User-Agent": self.user_agent}

    def iphai(self):
        urls = ["", "", "", ""]
        urls[0] = "http://www.iphai.com/free/ng"
        urls[1] = "http://www.iphai.com/free/np"
        urls[2] = "http://www.iphai.com/free/wg"
        urls[3] = "http://www.iphai.com/free/wp"
        for url in urls:
            r = requests.get(url, headers=self.header)
            r.encoding = 'utf-8'
            html = r.text
            tree = etree.HTML(html)
            trs = tree.xpath('//tr')
            tr=trs[1:]
            for i in tr:
                td = i.xpath("./td/text()")[:2]
                ip=str(td[0]).strip()
                port=str(td[1]).strip()
                ipport="http://"+ip+":"+port


if __name__ == "__main__":
    now = datetime.datetime.now()
    print ("Start at %s" % now)
    obj=getProxy()
    obj.iphai()