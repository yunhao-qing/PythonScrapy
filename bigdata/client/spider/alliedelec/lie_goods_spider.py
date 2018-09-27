from lxml import etree
import pika
import requests
from client.spider.base import Spider
import time

class LieGoodsSpider(Spider):
    def __init__(self, cat_id,goods_id,goods_name, goods_sn,site_url,goods_thumb,
            goods_desc,provider_name, ch, rk, is_first):
        Spider.__init__(self)

        self.cat_id = cat_id
        self.goods_id = goods_id
        self.goods_name = goods_name
        self.goods_sn = goods_sn
        self.goods_desc=goods_desc
        self.goods_thumb=goods_thumb
        self.provider_name=provider_name
        self.url = site_url

        self.ch = ch
        self.rk = rk
        self.is_first = is_first
        self.headers = {"User-Agent": "Mozilla/5.0 (compatible; MSIE 9.0;"+\
                "Windows NT 6.1; Trident/5.0)"}

    def goods(self, proxy_queue):
        url=self.url
        return self.get_no_proxies(self.url, headers=self.headers, timeout=30)

    def parse_goods(self,html):
        if html is None:
            return
        et = etree.HTML(html)
        MOQ = ''
        multi = ''
        pdf_url = ''
        kc = 0
        stock = []
        try:
            MOQ = int(html.split('MinimumOrderQuantity">')[1].split('</span>')[0])
        except:
            MOQ = 0
        try:
            multi = int(html.split('RequiredMultiples">')[1].split('</span>')[0])
        except:
            multi = 0
        try:
            pdf_url = et.xpath("//div[@id='divResources']/p/a/@href")[0]
        except:
            pdf_url = ""
        try:
            kc = int(html.split('StockQuantity" class="bold">')[1].\
                    split('</span>')[0])
        except:
            kc = 0
        uniqueno = html.split('lAlliedStockNumber">')[1].split('</span>')[0]
        goods_img = "http://www.alliedelec.com/images/products/Small/" +\
                uniqueno + ".jpg"

        stock.append(MOQ)
        stock.append(kc)
        tiered = []
        try:
            trs = et.xpath("//table[@class='price']/tr")
            count = 0
            for tr in trs:
                amount = tr.xpath("./td/text()")[0]
                price = tr.xpath("./td/text()")[1]
                tiered.append([int(amount), float(price[0])])
        except:
            pass
        print(MOQ, multi, pdf_url, stock, goods_img, tiered)


        #　若是第一次更新
        if self.is_first:
            # ********************************************* brand
            #TODO
            lieBrand = {
                'brand_name': self.provider_name,
                'site_url': '',
                'brand_logo': '',
                'brand_desc': '',
                'web_url': ''
            }
            body = str({"3": lieBrand})
            print('Sent 3. 更新lie_brand', body)
            self.ch.basic_publish(exchange='',
                    routing_key=self.rk,
                    properties=pika.BasicProperties(
                        delivery_mode=2),
                    body=body)
            body = ''


            # ********************************************** goods
            lg = {
                'goods_id': self.goods_id,
                'goods_sn': self.goods_sn,
                'provider_name': self.provider_name,
                'goods_name': self.goods_name,
                'goods_desc': self.goods_desc,
                'site_url': self.url,
                'goods_img': goods_img,
                'goods_name_style': '+',
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

            body = {'price': str(goods_price),
                    'goods_id': self.goods_id}
            body = str({"4": body})
            self.ch.basic_publish(exchange='',
                    routing_key=self.rk,
                    properties=pika.BasicProperties(
                        delivery_mode = 2),
                    body=body)
            body = ''

            # 更新mongo
            # ********************************************** allied
            allied = dict()
            allied['goods_id'] = self.goods_id
            allied['goods_name'] = self.goods_name
            allied['goods_sn'] = self.goods_sn
            allied['brand_name'] = self.provider_name
            allied['desc'] = self.goods_desc
            allied['docurl'] = pdf_url
            allied['pn'] = 'alliedelec'
            allied['MOQ'] = MOQ
            allied['pdf_url']=pdf_url
            allied['goods_img']=goods_img
            allied['stock'] = stock
            allied['tiered'] = tiered
            allied['increment'] = multi
            allied['time'] = int(time.time())
            allied['url'] = self.url
            body = str({"2": allied})
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
            allied = dict()
            allied['goods_id'] = self.goods_id
            allied['goods_name'] = self.goods_name
            allied['goods_sn'] = self.goods_sn
            allied['brand_name'] = self.provider_name
            allied['desc'] = self.goods_desc
            allied['docurl'] = pdf_url
            allied['pn'] = 'alliedelec'
            allied['MOQ'] = MOQ
            allied['pdf_url']=pdf_url
            allied['goods_img']=goods_img
            allied['stock'] = stock
            allied['tiered'] = tiered
            allied['increment'] = multi
            allied['time'] = int(time.time())
            allied['url'] = self.url
            body = str({"2": allied})
            print('Sent 2. 更新mongo', body)
            self.ch.basic_publish(exchange='',
                    routing_key=self.rk,
                    properties=pika.BasicProperties(
                        delivery_mode = 2),
                    body=body)

if __name__ == '__main__':
    #测试
    params = {'cat_id': 1,
              'goods_id': 1,
              'goods_name': 'LA5FF431',
              'goods_sn': 'LA5FF431&70300118',
              'site_url': 'http://www.alliedelec.com/schneider-electric-la5ff431/70300118/',
              'goods_thumb': ' http://www.alliedelec.com/images/products/Thumbnails/70300118_thumb.jpg',
              'goods_desc':'Electric Contactor Contact For Use WithLC1F150,   LCF115 Series',
              'provider_name':'Schneider Electric'}
    from client.recv_cron.allied import recv_goods
    conn = recv_goods.get_rb_conn()
    ch = conn.channel()
    rk = 'allied_store_goods'
    ch.queue_declare(queue=rk)
    lgs = LieGoodsSpider(params['cat_id'],
            params['goods_id'],
            params['goods_name'],
            params['goods_sn'],
            params['site_url'],
            params['goods_thumb'],
            params['goods_desc'],
            params['provider_name'],
            ch, rk, is_first=False)
    html = lgs.goods()
    lgs.parse_goods(html)

