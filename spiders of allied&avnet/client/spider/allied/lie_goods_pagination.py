import requests
import pika
import threading
from lxml import etree

lock = threading.Lock()

from client.spider.base import Spider


class LieGoodsPagnationSpider(Spider):
    def __init__(self, ch, rk,cat_id,url):
        Spider.__init__(self)
        self.cat_id=cat_id
        self.url=url
        self.rk = rk
        self.ch = ch
        self.headers = {"User-Agent": "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0)"}

    def get_total_pages(self):
        url = self.url
        try:
            r = requests.get(url, timeout=30)
            if r.status_code == 200:
                r.encoding = 'utf-8'
                return r.text
            else:
                r = requests.get(url, timeout=30,
                        proxies=self.proxies())
                if r.status_code == 200:
                    r.encoding = 'utf-8'
                    return r.text
                return None
        except Exception as e:
            print('10秒连接超时，切换代理IP')
            r = requests.get(url, timeout=30,
                        proxies=self.proxies())
            if r.status_code == 200:
                r.encoding = 'utf-8'
                return r.text
            return None

    def parse_get_total_pages(self, html):
        if html is None:
            return
        total_page = html.split('lnlTotalNumberOfPages_BOTTOM">')[1].split('</span>')[0]
        # 获取总页数
        body = str({"1": {'cat_id': self.cat_id, 'page_count': total_page}})

        print('Sent ', body)
        self.ch.basic_publish(exchange='', routing_key=self.rk,
                properties = pika.BasicProperties(delivery_mode=2),
                body=body)

    def pagnation(self, page):
        url = str(self.url+"?page="+str(page))
        try:
            r = requests.get(url, timeout=30)
            if r.status_code == 200:
                r.encoding = 'utf-8'
                return r.text
            else:
                r = requests.get(url, timeout=30,
                        proxies=self.proxies)
                if r.status_code == 200:
                    r.encoding = 'utf-8'
                    return r.text
                return None
        except Exception as e:
            r = requests.get(url, timeout=30,
                        proxies=self.proxies)
            if r.status_code == 200:
                r.encoding = 'utf-8'
                return r.text
            return None

    def parse_pagnation(self, html):
        html = etree.HTML(html)
        divs = html.xpath('//div[@class="OneLinkNoTx"]')
        for div in divs:
            try:
                site_url = "http://www.alliedelec.com" + div.xpath('./a/@href')[0]
            except:
                site_url=""
            try:
                onclick = div.xpath('./a/@onclick')[0]
            except:
                onclick = ""
            try:
                goods_desc = div.xpath('./a/text()')[0]
            except:
                goods_desc=""
            try:
                goods_name = onclick.split("'name': '")[1].split("', 'id': ")[0]
            except:
                goods_name=""
            try:
                provider_name = div.xpath('./a/b/text()')[0]
            except:
                provider_name=""
            try:
                uniqueno = onclick.split("'id': '")[1].split("', 'price':")[0]
            except:
                uniqueno=""
                goods_thumb = "http://www.alliedelec.com/images/products/Thumbnails/" + uniqueno + "_thumb.jpg"
            print(goods_name, uniqueno, goods_desc, goods_thumb, site_url, provider_name, self.cat_id)
            self.add_goods(goods_name, uniqueno, goods_desc, goods_thumb, site_url, provider_name, self.cat_id)

    def add_goods(self,goods_name, uniqueno,goods_desc, goods_thumb,site_url,provider_name,cat_id):
        #放入队列/MYSQL
        lg = dict()
        lg['pdf_url'] = ''
        lg['goods_thumb'] = goods_thumb
        lg['site_url'] = site_url

        lg['cat_id'] = cat_id
        lg['goods_sn'] = goods_name+"&"+uniqueno
        lg['goods_name'] = goods_name
        lg['provider_name'] = provider_name
        lg['goods_number'] = ''
        lg['min_buynum'] = ''
        lg['goods_brief'] = ''
        lg['goods_desc'] = goods_desc
        lg['goods_img'] = ''
        lg['series'] = ''
        lg['warehouse'] = ''
        lg['Encap'] = ''
        lg['Package'] = ''
        lg['HDT'] = ''
        lg['CDT'] = ''
        lg['goods_name_style'] = '+'

        body = str({'1': lg})
        with lock:
            self.ch.basic_publish(exchange='',
                    routing_key=self.rk,
                    properties=pika.BasicProperties(
                        delivery_mode = 2),
                    body=body)
        print('Sent', body)

if __name__ == '__main__':
    from client.recv_cron.allied import recv_pagnation
    conn = recv_pagnation.get_rb_conn()
    ch = conn.channel()
    qn = 'allied_store_pagnation'

    """从之前保存的分类得到每个搭配,只要二级分类！因为每个一级分类都有二级分类（cat_id和url，
    比如Electronic Enclosure，
    http://www.alliedelec.com/enclosures-racks-cabinets/electronic-enclosure/。
    之后）
    for each cat_id,cat_url:
        ..."""

    lgps = LieGoodsPagnationSpider(ch, qn,123, "http://www.alliedelec.com/automation-control/contactors/")


    html=lgps.get_total_pages()
    lgps.parse_get_total_pages(html)



