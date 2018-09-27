# -*- coding=utf-8 -*-
import requests
from lxml import etree
import pymongo

connection=pymongo.MongoClient('192.168.1.88',27017)
db=connection.ichunt
ip_list = db.ips3_66ip

class getProxy():
    def __init__(self):
        self.user_agent = "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0)"
        self.header = {"User-Agent": self.user_agent}

    def ip3366(self,num):
        nn_url = "http://www.ip3366.net/?stype=1&page="+ str(num)
        r = requests.get(nn_url, headers=self.header)
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
            print(td)
            td = tr.xpath('./td')[1]
            print(td)



    def loop_ip3366(self,page1,page2):
        for i in range(page1,page2):
            self.ip3366(i)
            print (i)

