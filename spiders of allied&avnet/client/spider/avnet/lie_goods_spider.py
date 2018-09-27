from lxml import etree
import pika
import requests
from client.spider.base import Spider
import time

class LieGoodsSpider(Spider):
    def __init__(self, cat_id,goods_id,goods_name, goods_sn,goods_desc, goods_thumb,site_url,
            ch, rk, is_first):
        Spider.__init__(self)

        self.cat_id = cat_id
        self.goods_id = goods_id
        self.goods_name = goods_name
        self.goods_sn = goods_sn
        self.goods_desc=goods_desc
        self.goods_thumb=goods_thumb
        self.url = site_url
        self.ch = ch
        self.rk = rk
        self.is_first = is_first
        self.headers = {"User-Agent": "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0)"}

    def goods(self):
        url=self.url
        try:
            r = requests.get(url,headers=self.headers, timeout=10)
            if r.status_code == 200:
                r.encoding = 'utf-8'
                return r.text
            else:
                r = requests.get(url, timeout=30, proxies=self.proxies())
                if r.status_code == 200:
                    r.encoding = 'utf-8'
                    return r.text
                return None
        except Exception as e:
            print('10秒连接超时，切换代理IP')
            r = requests.get(url, timeout=30, proxies=self.proxies())
            if r.status_code == 200:
                r.encoding = 'utf-8'
                return r.text
            return None

    def parse_goods(self,html):
        if html is None:
            return
        et = etree.HTML(html)
        manufacturer = str(et.xpath("//meta[@name='keywords']/@content")[0]).strip()
        try:
            stock = str(et.xpath("//span[@class='shipval']/text()")[0]).strip()
        except:
            stock = 0
        try:
            pdf_url = str(et.xpath("//a[@class='datasheet_align']/@href")[0]).strip()
        except:
            pdf_url = ""
        try:
            goods_img = str(et.xpath("//div[@id='outer-div1']/div/center/img/@src")[0]).strip()
        except:
            goods_img = ""
        tiered = []
        try:
            amount = str(et.xpath("//span[@class='usdpart1 usdpartHighlight']/span/text()")[0]).strip()
            price = str(et.xpath("//span[@class='usdpart1 usdpartHighlight']/p/text()")[0]).strip()
            tiered.append([amount, price])
        except:
            pass
        try:
            datas = et.xpath("//span[@class='usdpart1 ']")
            for data in datas:
                amount = str(data.xpath("./span/text()")[0]).strip()
                price = str(data.xpath("./p/text()")[0]).strip()
                tiered.append([amount, price])
        except:
            pass
        MOQ = str(et.xpath("//input[@id='quoteMin1']/@value")[0]).strip()
        multi = str(et.xpath("//input[@id='quoteMult1']/@value")[0]).strip()



        #　若是第一次更新
        if self.is_first:

            # ********************************************** goods
            lg = {
                'goods_id': self.goods_id,
                'goods_sn': self.goods_sn,
                'provider_name': manufacturer,
                'goods_name': self.goods_name,
                'goods_desc': self.goods_desc,
                'site_url': self.url,
            }
            body = str({"1": lg})
            print('Sent 1. 更新mysql', body)
            self.ch.basic_publish(exchange='',
                    routing_key=self.rk,
                    properties=pika.BasicProperties(
                        delivery_mode = 2),
                    body=body)
            body = ''

            # ********************************************** price

            goods_price = []
            for ti in tiered:
                tmp = {'purchases': ti[0], 'price': ti[1]}
                goods_price.append(tmp)

            body = {'goods_price': goods_price,
                    'goods_id': self.goods_id}
            body = str({"4": body})
            self.ch.basic_publish(exchange='',
                    routing_key=self.rk,
                    properties=pika.BasicProperties(
                        delivery_mode = 2),
                    body=body)
            body = ''

            # 更新mongo
            # ********************************************** avnet
            avnet = dict()
            avnet['goods_id'] = self.goods_id
            avnet['goods_name'] = self.goods_name
            avnet['goods_sn'] = self.goods_sn
            avnet['brand_name'] = manufacturer
            avnet['desc'] = self.goods_desc
            avnet['docurl'] = pdf_url
            avnet['pn'] = 'avnet'
            avnet['MOQ'] = MOQ
            avnet['pdf_url']=pdf_url
            avnet['goods_img']=goods_img
            avnet['stock'] = stock
            avnet['tiered'] = tiered
            avnet['increment'] = multi
            avnet['time'] = int(time.time())
            avnet['url'] = self.url
            body = str({"2": avnet})
            print('Sent 2. 更新mongo', body)
            self.ch.basic_publish(exchange='',
                    routing_key=self.rk,
                    properties=pika.BasicProperties(
                        delivery_mode = 2),
                    body=body)

        # 第二次更新
        else:

            # 更新mongo
            #TODO
            avnet = dict()
            avnet['goods_id'] = self.goods_id
            avnet['goods_name'] = self.goods_name
            avnet['goods_sn'] = self.goods_sn
            avnet['brand_name'] = manufacturer
            avnet['desc'] = self.goods_desc
            avnet['docurl'] = pdf_url
            avnet['pn'] = 'avnet'
            avnet['MOQ'] = MOQ
            avnet['pdf_url']=pdf_url
            avnet['goods_img']=goods_img
            avnet['stock'] = stock
            avnet['tiered'] = tiered
            avnet['increment'] = multi
            avnet['time'] = int(time.time())
            avnet['url'] = self.url
            body = str({"2": avnet})
            print('Sent 2. 更新mongo', body)
            self.ch.basic_publish(exchange='',
                    routing_key=self.rk,
                    properties=pika.BasicProperties(
                        delivery_mode = 2),
                    body=body)

if __name__ == '__main__':
    #信息格式如下
    params = {'cat_id': 1,
              'goods_id': 1,
              'goods_name': '',
              'goods_sn': '',
              'goods_desc': '',
              'goods_thumb':"",
              'site_url':""}
    from client.recv_cron.avnet import recv_goods
    conn = recv_goods.get_rb_conn()
    ch = conn.channel()
    rk = 'avnet_store_goods'
    ch.queue_declare(queue=rk)
    lgs = LieGoodsSpider(params['cat_id'],
            params['goods_id'],
            params['goods_name'],
            params['goods_sn'],
            params['goods_desc'],
            params['goods_thumb'],
            params['site_url'],
            ch, rk, is_first=False)
    html = lgs.goods()
    lgs.parse_goods(html)

