# -*- coding=utf-8 -*-
import requests
from lxml import etree
import pymongo
import time

# 0.连接数据库
connection = pymongo.MongoClient('192.168.1.88', 27017)
db = connection.ichunt
ip_list=db.ips

class getProxy():
    def __init__(self):
        self.user_agent = "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0)"
        self.header = {"User-Agent": self.user_agent}

    def xici(self, num):
        nn_url = "http://www.xicidaili.com/nn/" + str(num)
        try:
            r = requests.get(nn_url, headers=self.header,timeout = 30)
            r.encoding = 'utf-8'
            content = r.text
            et = etree.HTML(content)
            result_even = et.xpath('//tr[@class=""]')
            result_odd = et.xpath('//tr[@class="odd"]')

            for i in result_even:
                t1 = i.xpath("./td/text()")[:2]
                ip="http://"+t1[0]+":"+t1[1]
                raw_ips.append(ip)

            for i in result_odd:
                t2 = i.xpath("./td/text()")[:2]
                ip = "http://" + t2[0] + ":" + t2[1]
                raw_ips.append(ip)
        except:
            print("cannot open" + str(num))

    def loop_xici(self, page1, page2):
        for i in range(page1, page2):
            self.xici(i)
            print("xici")
            print(i)

    def xici2(self, num):
        nn_url = "http://www.xicidaili.com/nt/" + str(num)
        try:
            r = requests.get(nn_url, headers=self.header,timeout = 30)
            r.encoding = 'utf-8'
            content = r.text
            et = etree.HTML(content)
            result_even = et.xpath('//tr[@class=""]')
            result_odd = et.xpath('//tr[@class="odd"]')

            for i in result_even:
                t1 = i.xpath("./td/text()")[:2]
                ip="http://"+t1[0]+":"+t1[1]
                raw_ips.append(ip)

            for i in result_odd:
                t2 = i.xpath("./td/text()")[:2]
                ip = "http://" + t2[0] + ":" + t2[1]
                raw_ips.append(ip)
        except:
            print("cannot open" + str(num))

    def loop_xici2(self, page1, page2):
        for i in range(page1, page2):
            self.xici2(i)
            print("xici2")
            print(i)

    def nianshao(self,num):
        urls=["",""]
        urls[0] = "http://www.nianshao.me/?stype=1&page="+str(num)
        urls[1] = "http://www.nianshao.me/?stype=2&page=" + str(num)
        for url in urls:
            try:
                r = requests.get(url, headers=self.header,timeout = 30)
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
                    ipport=str(type+"://"+ip+":"+port).lower()
                    raw_ips.append(ipport)
            except:
                print("cannot open" + str(num))

    def loop_nianshao(self, page1, page2):
        for i in range(page1, page2):
            self.nianshao(i)
            print("nianshao")
            print(i)

    def ip66(self,num):
        nn_url = "http://www.66ip.cn/"+ str(num)+".html"
        try:
            r = requests.get(nn_url, headers=self.header,timeout = 30)
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
                ipport = str("http"+"://"+ip+":"+port)
                raw_ips.append(ipport)
        except:
            print("cannot open"+str(num))

    def loop_ip66(self,page1,page2):
        for i in range(page1,page2):
            self.ip66(i)
            print("ip66")
            print (i)

    def xsdaili(self, num):
        urls = ["", "", "", ""]
        urls[0] = "http://www.xsdaili.com/index.php?s=/index/mfdl/type/1/p/" + str(num) + ".html"
        urls[1] = "http://www.xsdaili.com/index.php?s=/index/mfdl/type/2/p/" + str(num) + ".html"
        urls[2] = "http://www.xsdaili.com/index.php?s=/index/mfdl/type/3/p/" + str(num) + ".html"
        urls[3] = "http://www.xsdaili.com/index.php?s=/index/mfdl/type/4/p/" + str(num) + ".html"
        for url in urls:
            try:
                r = requests.get(url, headers=self.header,timeout = 30)
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
                    ipport = str(type + "://" + ip + ":" + port).lower()
                    raw_ips.append(ipport)
            except:
                print("cannot open" + str(num))

    def loop_xsdaili(self,page1,page2):
        for i in range(page1,page2):
            self.xsdaili(i)
            print("xsdaili")
            print (i)

    def ipyqle(self):
        nn_url = "http://ip.yqie.com/ipproxy.htm"
        try:
            r = requests.get(nn_url, headers=self.header,timeout = 30)
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
                    raw_ips.append(ipport)
            print("ipyqle")
        except:
            print("cannot open"+"ipyqle")

    def iphai(self):
        urls = ["", "", "", ""]
        urls[0] = "http://www.iphai.com/free/ng"
        urls[1] = "http://www.iphai.com/free/np"
        urls[2] = "http://www.iphai.com/free/wg"
        urls[3] = "http://www.iphai.com/free/wp"
        for url in urls:
            try:
                r = requests.get(url, headers=self.header,timeout = 30)
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
                    raw_ips.append(ipport)
            except:
                print("cannot open"+"iphai")
        print("iphai")

    def ip181(self,num):
        nn_url = "http://www.ip181.com/daili/"+ str(num) +".html"
        try:
            r = requests.get(nn_url, headers=self.header,timeout = 30)
            r.encoding = 'utf-8'
            html = r.text
            et = etree.HTML(html)
            all = et.xpath('//tr')
            result=all[1:]

            for i in result:
                t = i.xpath("./td/text()")[:4]
                ipport = str("http" + "://" + t[0] + ":" + t[1])
                raw_ips.append(ipport)
        except:
            print("cannot open" + str(num))

    def loop_ip181(self,page1,page2):
        for i in range(page1,page2):
            self.ip181(i)
            print("ip181")
            print (i)

    def proxydb(self,num):
        nn_url = "http://proxydb.net/?protocol=http&offset="+ str(num*50)
        try:
            r = requests.get(nn_url, headers=self.header,timeout = 30)
            r.encoding = 'utf-8'
            html = r.text
            tree = etree.HTML(html)
            table = tree.xpath('//table[@class="table table-sm"]')
            table = table[0] if table else None
            tbody = table.xpath('./tbody')
            tbody = tbody[0] if tbody else None

            trs = tbody.xpath('./tr')
            for tr in trs:
                td = tr.xpath('./td')[0]
                raw_ipport = td.xpath('./a')[0].xpath('./text()')[0]
                ipport="http://"+raw_ipport
                raw_ips.append(ipport)
        except:
            print("cannot open" + str(num))

    def loop_proxydb(self,page1,page2):
        for i in range(page1,page2):
            self.proxydb(i)
            print("proxydb")
            print (i)

    def ip3366(self,num):
        nn_url = "http://www.ip3366.net/?stype=1&page="+ str(num)
        try:
            r = requests.get(nn_url, headers=self.header,timeout = 30)
            r.encoding = 'utf-8'
            html = r.text
            et = etree.HTML(html)
            all = et.xpath('//tr')
            result=all[1:]

            for i in result:
                t = i.xpath("./td/text()")[:4]
                ipport = str("http" + "://" + t[0] + ":" + t[1])
                raw_ips.append(ipport)
        except:
            print("cannot open" + str(num))

    def loop_ip3366(self,page1,page2):
        for i in range(page1,page2):
            self.ip3366(i)
            print("ip3366")
            print (i)

    def dlip(self, num):
        nn_url = "http://www.dlip.cn/gng/index_"+str(num)+".html"
        try:
            r = requests.get(nn_url, headers=self.header, timeout=30)
            r.encoding = 'utf-8'
            content = r.text
            et = etree.HTML(content)
            result = et.xpath('//tr')
            for i in result:
                try:
                    t = i.xpath("./td/text()")[:2]
                    ipport = str("http://" + t[0] + ":" + t[1])
                    raw_ips.append(ipport)
                except:
                    pass
        except:
            print("cannot open"+str(num))

    def loop_dlip(self,page1,page2):
        for i in range(page1,page2):
            self.dlip(i)
            print("dlip")
            print (i)

    def check_webs(self):
        for item in ip_list.find():
            raw_ips.append(item['ip'])
        print(len(raw_ips))
        self.iphai()
        self.loop_xici(1, 20) #20
        self.loop_xici2(1, 20)  # 20
        self.loop_nianshao(1,20) #20
        self.loop_ip66(1,10) #200
        self.loop_xsdaili(1,10) #62
        self.loop_ip181(1, 20) #882
        self.loop_proxydb(1, 91) #91 这个网页格式不规范 有时候会出问题
        self.ipyqle()
        self.loop_ip3366(1, 11)
        #self.loop_dlip(2,8)
        pure_ips = list(set(raw_ips))
        size=len(pure_ips)
        print(size)
        db.ips.remove()
        for i in range(size):
            ip_list.save({'ip':pure_ips[i]})

if __name__ == "__main__":
        raw_ips = []
        obj=getProxy()
        obj.check_webs()
        print("zzz done")
