# 每天更新增加的产品

from lxml import etree
from requests import get
import re
import threading
import logging
from client.spider.base import Spider
from client.spider.digikey.new_goods import lie_goods_spider

class NewGoodsSpider(Spider):
    def __init__(self, cat_id, url, channel, routing_key):
        Spider.__init__(self)
        self.cat_id = cat_id
        self.url = url
        self.channel = channel
        self.routing_key = routing_key

    def get_total_page(self, proxy_queue):
        return self.get_no_proxies(self.url, headers=self.headers, timeout=30)

    def parse_get_total_page(self, html, proxy_queue):
        if not html:
            return
        tree = etree.HTML(html)

        '''
        步骤:
        1. 先获取总页数
        3. 解析第一页的内容
        '''
        # 第1步 
        logging.debug('解析总页数')
        total_count = 0
        try:
            total_count = tree.xpath(
                    '//*[@id="content"]/div[9]/div[1]/div[2]/span/text()')[0]
            match = re.compile(r'/\d+[,]?\d+|/\d+')
            result = match.search(total_count)
            if result:
                result = result.group()
                total_count = int(''.join(result[1:].split(',')))

        except Exception as e:
            print(e)
            goods_sn = self.url.split('/')[-1]
            lgs = lie_goods_spider.LieGoodsSpider(
                cat_id=self.cat_id,
                goods_sn=goods_sn, 
                url=self.url,
                pdf_url='', 
                goods_thumb='',
                ch = self.channel,
                routingkey=self.routing_key)
            html = lgs.goods(proxy_queue)
            lgs.parse_goods(html)
            return

        logging.debug('总页数: %d\n' % total_count)
        # 2
        self.parse_next(html)

        tmp = self.url.split('?')
        base_url = tmp[0] + '/page/%d?newproducts=1'
        i = 2
        while i <= total_count:
            html = self.next(base_url % i, proxy_queue)
            self.parse_next(html)
            i += 1

    def next(self, url, proxy_queue):
        return self.get_no_proxies(url, headers=self.headers, timeout=30)

    def parse_next(self, html):
        if html is None:
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
        lg = dict()
        lg['pdf_url'] = pdf_url.encode().decode()
        lg['goods_thumb'] = img_url.encode().decode()
        lg['site_url'] = 'http://' + goods_detail_url
        
        lg['cat_id'] = self.cat_id
        lg['goods_sn'] = goods_detail_url.split('/')[-1]
        lgs = lie_goods_spider.LieGoodsSpider(
                    cat_id=lg['cat_id'],
                    goods_sn=lg['goods_sn'], 
                    url=lg['site_url'],
                    pdf_url=lg['pdf_url'], 
                    goods_thumb=lg['goods_thumb'],
                    ch = self.channel,
                    routingkey=self.routing_key)
        html = lgs.goods(proxy_queue)
        lgs.parse_goods(html)
