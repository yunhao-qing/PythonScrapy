from lxml import etree
from requests import get
import re
import logging
import threading

from client.spider.digikey.lie_goods_spider import LieGoodsSpider
from client.spider.base import Spider

lock = threading.Lock()

class LieGoodsPaginationSpider(Spider):
    '''
    PS. 首先得到分页规律 url, 总页数, 更新 lie_category的总页数字段
    >>from spider.digikey import LieGoodsPaginatonSpider
    >>cat_id = 20
    >>url = 'http://www.digikey.cn/products/zh/sensors-transducers/'+\
            'irda-transceiver-modules/538'
    >>lgps = LieGoodsPaginationSpider(cat_id, url)
    >>html = lgps.get_total_page()
    PS. 这里末日会将第一页的请求解析, 后面就不用重复请求一次了.
    >>lgps.parse_get_total_page(html)

    PS. 现在处理特定的某一页的解析请求
    >>cat_id = 20
    >>url = 'http://www.digikey.cn/products/zh/sensors-transducers/'+\
            'irda-transceiver-modules/538'
    >>page = 2
    >>lgps = LieGoodsPaginationSpider(cat_id, url)
    >>html = lgps.next(page)
    >>lgps.parse_next(html)
    '''

    def __init__(self, cat_id, url, channel, routingkey):
        Spider.__init__(self)
        self.cat_id = cat_id
        self.url = url
        self.headers = {}
        self.channel = channel
        self.routing_key = routingkey

    def get_total_page(self, proxy_queue):
        return self.get_no_proxies(self.url, headers=self.headers,
                timeout=30)

    def parse_get_total_page(self, html):
        global lock
        if not html:
            return
        tree = etree.HTML(html)

        '''
        步骤:
        1. 先获取总页数
        2. 然后找出分页的规律url
        3. 解析第一页的内容
        '''
        # 第1步 
        logging.debug('解析总页数')
        total_count = tree.xpath(
                '//*[@id="content"]/div[9]/div[1]/div[2]/span/text()')[0]
        match = re.compile(r'/\d+[,]?\d+|/\d+')
        result = match.search(total_count)
        if result:
            result = result.group()
            total_count = int(''.join(result[1:].split(',')))
        if not isinstance(total_count, int):
            '''
            lgs = LieGoodsSpider(cat_id=self.cat_id, goods_id=None,
                    goods_sn=None, url=self.url, pdf_url=None)
            html = lgs.goods()
            lgs.parse_goods(html)
            '''
            return

        logging.debug('总页数: %d\n' % total_count)

        with lock:
            body = str({'1': [self.cat_id, total_count]})
            self.channel.basic_publish(exchange='', routing_key=self.routing_key,
                    body=body)

        # 第3步
        self.parse_next(html)

    def next(self, page, proxy_queue):
        p_url = self.url + '/page/%d' % page
        return self.get_no_proxies(p_url, headers=self.headers, timeout=30)

    def parse_next(self, html):
        if not html:
            return
        tree = etree.HTML(html)
        t = tree.xpath('//tbody[@id="lnkPart"]')[0]
        logging.debug('产品列表表单 %s' % t)
        trs = t.xpath('./tr')
        for tr in trs:
            tds = tr.xpath('./td')
            a = tds[1].xpath('./a')
            if not a:
                pdf = '-'
            else:
                pdf = a[0].xpath('./@href')[0]

            pimg = tds[2].xpath('./a')[0].\
                    xpath('./img')[0].xpath('./@src')[0]
            gdurl = 'www.digikey.cn' + \
                    tds[3].xpath('./a')[0].xpath('./@href')[0]

            logging.debug('pdf: %s' % pdf)
            logging.debug('图像: %s' % pimg)
            logging.debug('产品详情: %s' % gdurl)
            self.add_goods(pdf, pimg, gdurl)

    def add_goods(self, pdf_url, img_url, goods_detail_url):
        global lock
        lg = dict()
        lg['pdf_url'] = pdf_url.encode().decode()
        lg['goods_thumb'] = img_url.encode().decode()
        lg['site_url'] = 'http://' + goods_detail_url
        
        lg['cat_id'] = self.cat_id
        lg['goods_sn'] = goods_detail_url.split('/')[-1]
        lg['goods_name'] = ''
        lg['provider_name'] = ''
        lg['goods_number'] = ''
        lg['min_buynum'] = 1
        lg['goods_brief'] = ''
        lg['goods_desc'] = ''
        lg['goods_img'] = ''
        lg['series'] = ''
        lg['warehouse'] = ''
        lg['Encap'] = ''
        lg['Package'] = ''
        lg['HDT'] = ''
        lg['CDT'] = ''
        lg['goods_name_style'] = '+'
        lg['is_check'] = 0
        
        with lock:
            body = str({'2': lg})
            self.channel.basic_publish(exchange='', routing_key=self.routing_key,
                    body=body)
