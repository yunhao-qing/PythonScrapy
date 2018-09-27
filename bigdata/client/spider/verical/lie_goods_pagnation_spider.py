from lxml import etree
import requests
import pika
import threading
lock = threading.Lock()

from client.spider.base import Spider

class LieGoodsPagnationSpider(Spider):
    def __init__(self, cat_id, keywords, ch, rk):
        Spider.__init__(self)
        self.keywords = keywords
        self.cat_id = cat_id
        self.ch = ch
        self.rk = rk
        self.api_url = 'https://www.verical.com/server-webapp/api/parametricSearch?catFilter=%s&currentSaleFilter=false&facetOn=true&format=json&maxResults=15&mfrFilter=&minQFilter=0&saleTypeFilter=&searchTerm=*&sortOn=&sortOrder=&startIndex=%d'
        self.headers = {
            'User-Agent': 'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.2; SV1; .NET CLR 1.1.4322)',
        }

    def get_total_pages(self, proxy_queue):
        url = self.api_url % (self.keywords, 0)
        return self.get_no_proxies(url, headers=self.headers, timeout=30)

    def parse_get_total_pages(self, html):
        if html is None:
            return
        html = html.replace('null', "''").replace('false', 'False').replace(
                'true', 'True')
        ci = eval(html)
        resultsReturned = ci['resultsReturned']
        print('总个数:', resultsReturned)

        total_page = resultsReturned // 15
        if resultsReturned % 15 != 0:
            total_page += 1
        body = str({"1": {'cat_id': self.cat_id, 'page_count': total_page}})

        print('Sent ', body)
        self.ch.basic_publish(exchange='', routing_key=self.rk,
                properties = pika.BasicProperties(delivery_mode=2),
                body=body)

    def pagnation(self, page):
        url = self.api_url % (self.keywords, (page-1)*15)
        return self.get_no_proxies(url, headers=self.headers , timeout=30)

    def parse_pagnation(self, html):
        if not html:
            return
        html = html.replace('false', 'False').replace('true', 'True').\
                replace('null', "''")

        hd = eval(html)
        try:
            views = hd['views']
            goods = []
            for good in views:
                goods_name = good['mpn']
                goods_thumb = good['partSmallImage']
                goods_img = good['partLargeImage']
                pdf_url = good['originalDataSheetURL']
                partId = good['partId']
                print('产品名称:', goods_name)
                print('小图片:', goods_thumb)
                print('大图片:', goods_img)
                print('pdf链接:', pdf_url)
                print('partId:', partId)
                self.add_goods(goods_name, goods_thumb, goods_img, pdf_url, partId)
        except Exception as e:
            print(e)

    def add_goods(self, goods_name, goods_thumb, goods_img, pdf_url, partId):
        lg = dict()
        lg['pdf_url'] = pdf_url.encode().decode()
        lg['goods_thumb'] = goods_thumb.encode().decode()
        lg['site_url'] = ''
        
        lg['cat_id'] = self.cat_id
        lg['goods_sn'] = goods_name + '€€' + str(partId)
        lg['goods_name'] = goods_name
        lg['provider_name'] = ''
        lg['goods_number'] = ''
        lg['min_buynum'] = 1
        lg['goods_brief'] = ''
        lg['goods_desc'] = ''
        lg['goods_img'] = goods_img
        lg['series'] = ''
        lg['warehouse'] = ''
        lg['Encap'] = ''
        lg['Package'] = ''
        lg['HDT'] = ''
        lg['CDT'] = ''
        lg['goods_name_style'] = '+'
        lg['is_check'] = 0
        
        body = str({'1': lg})
        with lock:
            self.ch.basic_publish(exchange='', routing_key=self.rk,
                    body=body)
        print('Sent', body)

if __name__ == '__main__':
    '''
    from client.recv_cron.verical import recv_pagnation

    conn = recv_pagnation.get_rb_conn()
    ch = conn.channel()
    qn = 'verical_store_get_total_pages'
    proxy_ip = 'proxy_ip_verical'
    ch.queue_declare(queue=qn)

    lgps = LieGoodsPagnationSpider(638, 'Unsorted', ch, qn)
    html = lgps.get_total_pages(proxy_ip)
    lgps.parse_get_total_pages(html)
    html = lgps.pagnation(1)
    lgps.parse_pagnation(html)
    '''
    print('OK')
