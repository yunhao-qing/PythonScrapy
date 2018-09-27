# -*- coding: utf-8 -*-

from lxml import etree
from requests import get
import logging
from db.company import mysql_client, mongo_client
from unittest import TestCase, main
import re
import time
import hashlib
import threading

lock = threading.Lock()

class LieGoodsSpider(object):
    def __init__(self, brand_id, cat_id, items_id, url):
        self.url = url
        self.headers = {
                'Host': 'www.microchipdirect.com',
                'Connection': 'keep-alive',
                'Cache-Control': 'max-age=0',
                'Upgrade-Insecure-Requests': '1',
                'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64)'+\
                        'AppleWebKit/537.36 (KHTML, like Gecko)'+\
                        'Ubuntu Chromium/55.0.2883.87 Chrome/'+\
                        '55.0.2883.87 Safari/537.36',
                'Accept': 'text/html,application/xhtml'+\
                        '+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Encoding': 'gzip, deflate, sdch',
                'Accept-Language': 'en-US,en;q=0.8'
                }

        if url.strip() == '':
            self.url = None
        else:
            self.brand_id = brand_id
            self.cat_id = cat_id
            self.items_id = items_id
            self.url = url

    def get_goods_detail(self):
        if not self.url:
            return None
        now = time.time()
        logging.debug('找到好东西了: 正在连接goods detail')
        r = get(self.url, headers=self.headers, timeout=30)
        status_code = r.status_code
        if status_code == 200:
            r.encoding = 'utf-8'
            html = r.text
            now = time.time() -now
            print('[%d] %s [time: %d]' % (status_code, self.url, now))
            return html
        else:
            now = time.time() -now
            print('[%d] %s [time: %d]' % (status_code, self.url, now))
            return None

    def parse_get_goods_detail(self, html):
        '''
        method: parse_get_goods_detail_init
        params: 
            html-type: str
            is_update_mongo-type: bool
            is_update_goods_id-typ: int

        '''
        if not html:
            return
        div_table_xpath = '//*[@id="jtooltip"]'
        row_div_xpath = './div'

        goods_name_xpath = '//span[@id="_ctl0_cphRightMaster_'+\
                'rptProducts__ctl%d_productIDLabelvalue"]/text()'
        buy_num_xpath = '//span[@id="_ctl0_cphRightMaster_'+\
                'rptProducts__ctl%d_ProductpriceStandard_'+\
                'rptPrices__ctl%d_lblRange"]/text()'
        price_xpath = '//span[@id="_ctl0_cphRightMaster_'+\
                'rptProducts__ctl%d_ProductpriceStandard_'+\
                'rptPrices__ctl%d_lblPrice"]/text()'
        kc_xpath = '//span[@id="_ctl0_cphRightMaster_rptProducts__' +\
                'ctl%d_ProductAvail_lblAvailibility"]/b/text()'

        tree = etree.HTML(html)
        div_table = tree.xpath(div_table_xpath)
        if not div_table:
            return
        else:
            div_table = div_table[0]

        row_divs = div_table.xpath('./div')

        i = 0
        while i < len(row_divs):
            j = 0

            goods_name = row_divs[i].xpath(goods_name_xpath % i)
            kc = row_divs[i].xpath(kc_xpath % i)
            if kc:
                kc = kc[0].lstrip().rstrip()
            else:
                kc = '0'

            lieGoods = mysql_client.LieGoods()
            if goods_name:
                goods_name = goods_name[0].lstrip().rstrip()
                logging.debug(goods_name)
                lieGoods['goods_name'] = goods_name
                lieGoods['brand_id'] = self.brand_id
                lieGoods['cat_id'] = self.cat_id
                lieGoods['items_id'] = self.items_id
                lieGoods['goods_sn'] = goods_name
                lieGoods['min_buynum'] = 1
                lieGoods['goods_desc'] = ''
            else:
                break

            goods_price = dict()
            while j >= 0:
                buy_num = row_divs[i].xpath(buy_num_xpath % (i, j))
                price = row_divs[i].xpath(price_xpath % (i, j))
                if buy_num and price:
                    buy_num = buy_num[0]
                    price = price[0]

                    buy_num = buy_num.lstrip().rstrip()

                    price = price.lstrip().rstrip()
                    buy_num = buy_num.split('-')[0]
                    if buy_num[-1:] == '+':
                        buy_num = buy_num[:-1]

                    price = price.split('-')[0]
                    goods_price[buy_num] = price

                    lieGoods['goods_sn'] += str(buy_num)
                    j += 1
                else:
                    lieGoods['goods_sn'] = lieGoods['goods_sn'].\
                            replace('\r','').replace('\n','').strip()
                    lieGoods['price'] = str(goods_price)
                    with lock:
                        self.update_goods_detail_in_mongo(lieGoods, kc)
                    break
            i += 1

    def update_goods_detail_in_mongo(self, lieGoods, kc):
        global lock
        md5 = hashlib.md5()
        md5.update(lieGoods['goods_sn'].encode())
        goods_sn_md5 = md5.hexdigest()
        lieGoods['goods_sn'] = goods_sn_md5

        # 判断在mongo里是否存在
        is_exist = mongo_client.Company.getCompany_by_goods_sn(goods_sn_md5)
        if is_exist:
            print('替换mongo里的数据')
            #存在就替换
            goods_id = is_exist['goods_id']
            company = self.fz_goods_detail(lieGoods, goods_id, kc)
            mongo_client.Company.replace_one_by_goods_id(
                    goods_id, company)
        else:
            print('增加mysql,mongo里的数据')
            #不存在就查询Mysql是否存在
            goods_id = mysql_client.LieGoods.get_goods_id_by_goods_sn(
                    goods_sn_md5)
            if not goods_id:
                print('\t该数据不存在, 增加数据到mysql')
                # mysql里不存在,增加
                mysql_client.LieGoods.addLieGoods(lieGoods)
                # 查询是否增加成功
                goods_id = mysql_client.LieGoods.\
                        get_goods_id_by_goods_sn(goods_sn_md5)
                if goods_id:
                    print('\t\t增加数据到mysql成功')
                    #成功
                    company = self.fz_goods_detail(lieGoods, goods_id, kc)
                    # 增加Mongo
                    print('\t\t\t增加数据到Mongo')
                    print(company)
                    mongo_client.Company.addCompany(company)
                else:
                    print('\t\t增加数据到mysql失败')
            else:
                #mysql里已存在
                print('\t该数据已存在，增加Mongo')
                company = self.fz_goods_detail(lieGoods, goods_id, kc)
                #增加Mongo
                print(company)
                mongo_client.Company.addCompany(company)

    def fz_goods_detail(self, lieGoods, goods_id, kc):
        kc = int(''.join(kc.split(',')))
        company = mongo_client.Company()
        company['goods_id'] = goods_id
        company['goods_name'] = lieGoods['goods_name']
        company['goods_sn'] = lieGoods['goods_sn']
        company['brand_name'] = 'microchip'
        company['desc'] = ''
        company['docurl'] = ''
        company['pn'] = 'company'

        price_dict = eval(lieGoods['price'])
        ttmp = []
        for k in price_dict.keys():
            if k.isdigit():
                ttmp.append(int(k))
        ttmp.sort()
        company['stock'] = [ttmp[0], kc]
        
        tired =  [] 
        for k in ttmp:
            tired.append([k, float(price_dict[str(k)])])

        company['tiered'] = tired
        company['increment'] = 1
        company['time'] = int(time.time())
        company['url'] = self.url
        return company

    def add_lie_goods_price(self, goods_id, price):
        price = mysql_client.LieGoodsPrice.\
                get_price_by_goods_id(goods_id)
        if not price:
            lieGoodsPrice = mysql_client.\
                    LieGoodsPrice()            
            lieGoodsPrice['goods_id'] = goods_id
            lieGoodsPrice['price'] = str(price)
            mysql_client.LieGoodsPrice.\
                    addLieGoodsPrice(lieGoodsPrice)

class Test(TestCase):
    def test_lgs(self):
        brand_id = 14
        items_id = 12155
        cat_id = 1014
        url = 'http://www.microchipdirect.com/ProductDetails.aspx?Category=ATtiny10'
        self.lgs = LieGoodsSpider(
                cat_id=cat_id, url=url, brand_id=brand_id, items_id=items_id)
        html = self.lgs.get_goods_detail()
        self.lgs.parse_get_goods_detail(html)

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    main()
