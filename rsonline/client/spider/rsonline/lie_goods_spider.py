from lxml import etree
import pika
import requests
from client.spider.base import Spider
import time
import traceback

class LieGoodsSpider(Spider):
    def __init__(self, cat_id, goods_id, goods_name, goods_sn, site_url, provider_name,
                 goods_thumb,goods_img,goods_desc,ch, rk, is_first):
        Spider.__init__(self)
        self.cat_id = cat_id
        self.goods_id = goods_id
        self.goods_name = goods_name
        self.goods_sn = goods_sn
        self.url = site_url
        self.provider_name = provider_name
        self.goods_thumb=goods_thumb
        self.goods_img=goods_img
        self.goods_desc=goods_desc
        self.ch = ch
        self.rk = rk
        self.is_first = is_first
        self.headers = {
            'User-Agent': 'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.2; SV1; .NET CLR 1.1.4322)',
        }

    def goods(self):
        print('正在访问详情页')
        trycount=0
        while (trycount<5):
            try:
                url = self.url
                r = requests.get(url, headers=self.headers,timeout=50)
                if r.status_code==200:
                    html = r.content
                    html1 = r.text
                    return html, html1
                else:
                    trycount+=1
            except:
                trycount +=1
        print("失败了",self.url)


    def parse_goods(self, html,html1):
        if html is None:
            return
        try:
            et = etree.HTML(html)
            tiered = []
            qdl = int(et.xpath('//input[@id = "breakRangeDifference"]/@value')[0])
            pdf_url = ''
            try:
                reflinks = et.xpath('//div[@class="techRefLink"]/a')
                for reflink in reflinks:
                    refname = reflink.xpath('./text()')[0]
                    if refname == "Datasheet":
                        pdf_url = reflink.xpath('./@onclick')[0]
                        pdf_url = pdf_url.split("('")[1].split("')")[0]
                    else:
                        pass
            except:
                pdf_url = ''

            if "现货库存" in html1:
                # 现货库存
                internal_kc = et.xpath('//div[@class="floatLeft stockMessaging availMessageDiv'
                                       ' bottom5"]/text()')[0].split(" ")[0]
                if "海外库存" in html1 and not "需要清关" in html1:
                    # 海外库存
                    external_kc = et.xpath('//div[@class="floatLeft availMessageDiv bottom5"]'
                                           '/text()')[0].split(" ")[0]
                else:
                    external_kc = 0
            else:
                internal_kc = 0
                external_kc = 0

            print("pdf:", pdf_url)
            print("本地库存：", internal_kc)
            print("国外库存：", external_kc)
            print("起订量：", qdl)

            divs = et.xpath('//div[@id="break-prices-list"]/div[@class="value-row"]')
            if len(divs) > 1:
                for div in divs:
                    quantity = div.xpath('./div[@class="breakRangeWithoutUnit"]/span/@content')[0]
                    unitPrice = div.xpath('./div[@class="unitPrice"]/span[@itemprop="price"]/@content')[0]
                    unitPrice = unitPrice.replace(",", "")
                    tiered.append([int(quantity), float(unitPrice)])
            elif len(divs) == 1:
                price = et.xpath('//span[@itemprop="price"]/@content')[0]
                price = price.replace(",", "")
                tiered.append([1, float(price)])

            print(tiered)
        except Exception as e:
            print('解析异常', e)
            exstr = traceback.format_exc()
            with open('/data/log/bigdata/rsonline/解析异常.txt', 'a', encoding='utf-8') as f:
                f.write(time.ctime() + ':' + self.url + '\n' + exstr + '\n')
            return

        try:
            #　若是第一次更新
            if self.is_first:
                #更新mysql
                # ********************************************* brand
                lieBrand = {
                    'brand_name': self.provider_name,
                    'site_url': self.url,
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
                    'goods_name_style': self.goods_name,
                    'goods_desc': self.goods_desc,
                    'site_url': self.url,
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
                        'goods_id': self.goods_id}
                body = str({"4": body})
                print('Sent 4. 更新lie_goods_price_n', body)
                self.ch.basic_publish(exchange='',
                        routing_key=self.rk,
                        properties=pika.BasicProperties(
                            delivery_mode = 2),
                        body=body)
                body = ''

                # 更新mongo
                # ********************************************** rsonline
                rsonline = dict()
                rsonline['goods_id'] = self.goods_id
                rsonline['goods_name'] = self.goods_name
                rsonline['goods_sn'] = self.goods_sn
                rsonline['brand_name'] = self.provider_name
                rsonline['desc'] = self.goods_desc
                rsonline['docurl'] =pdf_url
                rsonline['pn'] = 'rsonline'
                rsonline['stock'] = [qdl, internal_kc,external_kc]
                rsonline['tiered'] = tiered
                rsonline['increment'] = 1
                rsonline['time'] = int(time.time())
                rsonline['url'] = self.url
                body = str({"2": rsonline})
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
                rsonline = dict()
                rsonline['goods_id'] = self.goods_id
                rsonline['goods_name'] = self.goods_name
                rsonline['goods_sn'] = self.goods_sn
                rsonline['brand_name'] = self.provider_name
                rsonline['desc'] = self.goods_desc
                rsonline['docurl'] = pdf_url
                rsonline['pn'] = 'rsonline'
                rsonline['stock'] = [qdl, internal_kc,external_kc]
                rsonline['tiered'] = tiered
                rsonline['increment'] = 1
                rsonline['time'] = int(time.time())
                rsonline['url'] = self.url
                body = str({"2": rsonline})
                print('Sent 2. 更新mongo', body)
                self.ch.basic_publish(exchange='',
                        routing_key=self.rk,
                        properties=pika.BasicProperties(
                            delivery_mode = 2),
                        body=body)
        except Exception as e:
            print('推送异常', e)
            exstr = traceback.format_exc()
            with open('/data/log/bigdata/rsonline/推送异常.txt', 'a', encoding='utf-8') as f:
                f.write(time.ctime() + ':' + self.url + '\n' + exstr + '\n')

if __name__ == '__main__':
    params = {
            'cat_id': 666,
            'goods_id': 6666666,
            'goods_name': '666666',
            'goods_sn': '666666666666',
            'site_url': "http://china.rs-online.com/web/p/differential-pressure-sensor-ics/1218196/",
            'provider_name':'Honeywell',
            'goods_thumb':"66",
            'goods_img':"666",
            'goods_desc':'666666'

    }
    from client.recv_cron.rsonline import recv_goods
    conn = recv_goods.get_rb_conn()
    ch = conn.channel()
    rk = 'rsonline_store_goods'
    ch.queue_declare(queue=rk)
    lgs = LieGoodsSpider(params['cat_id'],
            params['goods_id'],
            params['goods_name'],
            params['goods_sn'],
            params['site_url'],
            params['provider_name'],
            params['goods_thumb'],
            params['goods_img'],
            params['goods_desc'],
            ch, rk, is_first=True)
    html,html1 = lgs.goods()
    lgs.parse_goods(html,html1)
