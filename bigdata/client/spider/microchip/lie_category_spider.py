from lxml import etree
from requests import get
from db.company import mysql_client

import logging
from unittest import TestCase, main
import sys, os

class LieCategorySpider(object):
    def __init__(self):
        self.url = 'http://www.microchip.com'
        self.headers = {
                'Accept':'text/html,application/xhtml+xml,' +\
                        'application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Encoding': 'gzip, deflate, sdch',
                'Accept-Language': 'en-US,en;q=0.8',
                'Connection': 'keep-alive',
                'Host': 'www.microchip.com',
                'Upgrade-Insecure-Requests': '1',
                'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) ' +\
                        'AppleWebKit/537.36 (KHTML, like Gecko) ' +\
                        'Ubuntu Chromium/55.0.2883.87 '+\
                        'Chrome/55.0.2883.87 Safari/537.36'}
        self.brand_name = 'microchip'

        self.brand_id = mysql_client.LieBrand.get_brand_id_by_brand_name(
                self.brand_name)
        if not self.brand_id:
            lieBrand = mysql_client.LieBrand()
            lieBrand['brand_name'] = self.brand_name
            lieBrand['brand_desc'] = 'microchip.com'
            lieBrand['site_url'] = self.url
            mysql_client.LieBrand.addLieBrand(lieBrand)
            self.brand_id = mysql_client.LieBrand.get_brand_id_by_brand_name(
                self.brand_name)
        logging.debug('蠕啊蠕啊小小鱼 %d' % self.brand_id)

    def get_all_category(self):
        r = get(self.url, headers=self.headers)
        status_code = r.status_code
        if status_code == 200:
            r.encoding = 'utf-8'
            html = r.text
            return html
        else:
            return None

    def parse_get_all_category(self, html):
        if not html:
            return
        tree = etree.HTML(html)
        column_xpath = '//*[@id="Form1"]/header/div[3]' +\
                '/div[1]/div[@class="three columns ac"]'
        for div in tree.xpath(column_xpath):
            ul = div.xpath('./ul')[0]
            for li in ul.xpath('./li'):
                cat_name = li.xpath(
                        './a/text()')[0].encode().decode()
                url = li.xpath('./a/@href')[0].encode().decode()
                level = 0
                parent_id = 0
                islast = 0
                ext_fields = ''
                lc_0 = self.new_lieCategory(
                        cat_name, url, level, parent_id, islast, ext_fields)

                cat_id = mysql_client.LieCategory.\
                        get_cat_id_by_cat_name_brand_id(
                                lc_0['cat_name'], self.brand_id)
                if not cat_id:
                    mysql_client.LieCategory.addLieCategory(lc_0)

                for li_1 in li.xpath('./ul/li'):
                    cat_name = li_1.xpath('./a/text()')[0].encode().decode()
                    tmp = li_1.xpath('./a/@href')
                    url = tmp[0].encode().decode() if len(tmp) != 0 else ''
                    level = 1
                    parent_id = lc_0['cat_name']
                    islast = 1
                    ext_fields = ''
                    lc_1 = self.new_lieCategory(
                            cat_name, url, level, parent_id, 
                            islast, ext_fields)
                    self.add_lieCategory(lc_1)

                    for li_2 in li_1.xpath('./ul/li'):
                        cat_name = li_2.xpath('./a/text()')[0].encode().decode()
                        tmp = li_2.xpath('./a/@href')
                        url = tmp[0].encode().decode() if len(tmp) != 0 else None
                        level = 1
                        parent_id = lc_1['cat_name']
                        islast = 1
                        ext_fields = ''
                        lc_2 = self.new_lieCategory(
                                cat_name, url, level, parent_id, 
                                islast, ext_fields)
                        self.add_lieCategory(lc_2)

    def add_lieCategory(self, lieCategory):
        parent_id = mysql_client.LieCategory.\
                get_cat_id_by_cat_name_brand_id(
                        lieCategory['parent_id'], self.brand_id)
        lieCategory['parent_id'] = parent_id

        cat_id = mysql_client.LieCategory.\
                get_cat_id_by_cat_name_brand_id(
                        lieCategory['cat_name'], self.brand_id)
        if not cat_id:
            mysql_client.LieCategory.addLieCategory(lieCategory)

    def new_lieCategory(self, cat_name, url, level, parent_id, islast,
            ext_fields):
        lc = mysql_client.LieCategory()
        lc['brand_id'] = self.brand_id
        lc['url'] = self.url + url.lstrip().rstrip()
        if 'Overview' in cat_name:
            lc['cat_name'] = ','.join(
                    [parent_id, cat_name.lstrip().rstrip()])
        else:
            lc['cat_name'] = cat_name
        lc['level'] = level
        lc['parent_id'] = parent_id
        lc['islast'] = islast
        lc['ext_fields'] = ext_fields
        return lc
        
class LieCategorySpiderTest(TestCase):
    def test_init(self):
        self.assertRaises(Exception, LieCategorySpider())

    def test_get_all_category(self):
        lieCategorySpider = LieCategorySpider()
        html = lieCategorySpider.get_all_category()
        self.assertNotEqual(None, html)
        lieCategorySpider.parse_get_all_category(html)

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    main()
