from lxml import etree 
import pika
import requests
from client.spider.base import Spider
import time
import traceback

class LieGoodsSpider(Spider):
    def __init__(self, cat_id, goods_id, goods_name, goods_sn, url, pdf_url, 
            ch, rk, is_first):
        Spider.__init__(self)
        self.cat_id = cat_id
        self.goods_id = goods_id
        self.goods_name = goods_name
        self.goods_sn = goods_sn
        self.url = url
        self.pdf_url = pdf_url
        self.ch = ch
        self.rk = rk
        self.is_first = is_first
        self.partId = goods_sn.split('€€')[1].split('_')[0]
        self.api_url = 'https://www.verical.com/server-webapp/'+\
                'api/getCatalogItems?format=json&includeAltern'+\
                'ates=false&mpnIDs=%s&t=1491444986908'
        self.headers = {
            'User-Agent': 'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.2;'+\
                    'SV1; .NET CLR 1.1.4322)',
        }


    def goods(self,proxy_queue):
        url = self.api_url % self.partId
        return self.get_no_proxies(url, headers=self.headers, timeout=30)

    def parse_goods(self, html):
        if html is None:
            return
        try:
            html = html.replace('null', "''").replace('false', 'False').\
                    replace('true', 'True')
            data = eval(html)
            its = data['itemsViewList']
            manufacturer = ''
            desc = ''
            site_url = self.api_url % self.partId
            tiered = [] 
            qdl = 0
            kc = 0

            sig = -1
            if '_' in self.goods_sn:
                sig = int(self.goods_sn.split('_')[1]) # goods_sn的标志位
            g_count = 0
            for it in its:
                if sig != -1 and g_count != sig and g_count < sig:
                    g_count += 1
                    continue
                manufacturer = it['manufacturer'] # 供应商
                desc =  it['description']
                kc = it['quantity']

                tierViewList = it['tieredPricingView']['tierViewList']
                qdl = it['minimumOrderQuantity']
                count = 0
                for tvl in tierViewList:
                    tiered.append([tvl['minimumOrderQuantity'], tvl['unitPrice']])
                if tiered == []:
                    unitPrice = it['unitPrice']
                    tiered.append([kc, unitPrice])

                goods_sn_tmp = self.goods_sn
                if g_count != 0 and '_' not in self.goods_sn:
                    self.goods_id = -1
                    goods_sn_tmp = self.goods_sn + '_%d' % g_count
                # 如果是新的卖家 -----------------------------------------------
                if g_count > 0 and sig == -1 and self.is_first == False:
                    #更新mysql
                    # ********************************************* brand
                    lieBrand = {
                        'brand_name': manufacturer,
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
                        'goods_sn': goods_sn_tmp,
                        'provider_name': manufacturer,
                        'goods_name_style': self.goods_name,
                        'goods_desc': desc,
                        'site_url': site_url,
                        'is_check': 0,
                    }
                    body = str({"1": lg})
                    print('Sent 1. 更新lie_goods', body)
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
                            'goods_id': self.goods_id,
                            'goods_sn': self.goods_sn}
                    body = str({"4": body})
                    print('Sent 4. 更新lie_goods_price_n', body)
                    self.ch.basic_publish(exchange='',
                            routing_key=self.rk, 
                            properties=pika.BasicProperties(
                                delivery_mode = 2),
                            body=body)
                    body = ''

                #　若是第一次更新 ----------------------------------------------
                if self.is_first:
                    #更新mysql
                    # ********************************************* brand
                    lieBrand = {
                        'brand_name': manufacturer,
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
                        'goods_sn': goods_sn_tmp,
                        'provider_name': manufacturer,
                        'goods_name_style': self.goods_name,
                        'goods_desc': desc,
                        'site_url': site_url,
                        'is_check': 0,
                    }
                    body = str({"1": lg})
                    print('Sent 1. 更新lie_goods', body)
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
                            'goods_id': self.goods_id,
                            'goods_sn': self.goods_sn}
                    body = str({"4": body})
                    print('Sent 4. 更新lie_goods_price_n', body)
                    self.ch.basic_publish(exchange='',
                            routing_key=self.rk, 
                            properties=pika.BasicProperties(
                                delivery_mode = 2),
                            body=body)
                    body = ''

                    # 更新mongo
                    # ********************************************** verical
                    verical = dict()
                    verical['goods_id'] = self.goods_id
                    verical['goods_name'] = self.goods_name
                    verical['goods_sn'] = goods_sn_tmp
                    verical['brand_name'] = manufacturer
                    verical['desc'] = desc
                    verical['docurl'] = self.pdf_url
                    verical['pn'] = 'verical'
                    verical['stock'] = [qdl, kc]
                    verical['tiered'] = tiered
                    verical['increment'] = 1
                    verical['time'] = int(time.time())
                    verical['url'] = site_url
                    body = str({"2": verical})
                    print('Sent 2. 更新mongo', body)
                    self.ch.basic_publish(exchange='',
                            routing_key=self.rk,
                            properties=pika.BasicProperties(
                                delivery_mode = 2),
                            body=body)

                # 第二次更新 --------------------------------------------------
                else:
                    # 更新mongo
                    #TODO
                    verical = dict()
                    verical['goods_id'] = self.goods_id
                    verical['goods_name'] = self.goods_name
                    verical['goods_sn'] = goods_sn_tmp
                    verical['brand_name'] = manufacturer
                    verical['desc'] = desc
                    verical['docurl'] = self.pdf_url
                    verical['pn'] = 'verical'
                    verical['stock'] = [qdl, kc]
                    verical['tiered'] = tiered
                    verical['increment'] = 1
                    verical['time'] = int(time.time())
                    verical['url'] = site_url
                    body = str({"2": verical})
                    print('Sent 2. 更新mongo', body)
                    self.ch.basic_publish(exchange='',
                            routing_key=self.rk,
                            properties=pika.BasicProperties(
                                delivery_mode = 2),
                            body=body)

                tiered = []
                g_count += 1
        except Exception as e:
            print('解析异常', e)
            exstr = traceback.format_exc()
            print(exstr)
            '''
            with open('/data/log/bigdata/verical/解析异常.txt', 'a', encoding='utf-8') as f:
                f.write(time.ctime() + ':' + self.url + '\n' + exstr + '\n')
            '''
            return 
        # 如果商家已删除 -------------------------------------------------------
        if g_count < sig+1 and sig != -1:
            # 返回404
            # 更新mongo
            verical = dict()
            verical['goods_id'] = self.goods_id
            verical['goods_name'] = self.goods_name
            verical['goods_sn'] = self.goods_sn
            verical['brand_name'] = manufacturer
            verical['desc'] = desc
            verical['docurl'] = self.pdf_url
            verical['pn'] = 'verical'
            verical['stock'] = []
            verical['tiered'] = []
            verical['increment'] = 1
            verical['time'] = int(time.time())
            verical['url'] = site_url
            verical['is_error'] = 404
            body = str({"2": verical})
            print('Sent 2. 更新mongo', body)
            self.ch.basic_publish(exchange='',
                    routing_key=self.rk,
                    properties=pika.BasicProperties(
                        delivery_mode = 2),
                    body=body)

if __name__ == '__main__':
    params = {
        'cat_id': 601,
        'goods_id': 17001584836, 
        'goods_name': 'DM160218', 
        'goods_sn': 'DM160218€€777068', 
        'site_url': '',
        'pdf_url': 'http://download.siliconexpert.com/pdfs/2013/11/21/7/45/33/280/mcp_/manual/html_productsearch.aspxkeywordsdm160218.aspxkeywordsdm160218.pdf'
    }
    from client.recv_cron.verical import recv_goods
    conn = recv_goods.get_rb_conn()
    ch = conn.channel()
    rk = 'verical_store_goods'
    proxy_queue = 'proxy_ip_verical'
    ch.queue_declare(queue=rk, durable=True)
    lgs = LieGoodsSpider(params['cat_id'], 
            params['goods_id'], 
            params['goods_name'], 
            params['goods_sn'],
            params['site_url'], 
            params['pdf_url'],
            ch, rk, is_first=True)
    html = lgs.goods(proxy_queue)
    lgs.parse_goods(html)
    conn.close()
