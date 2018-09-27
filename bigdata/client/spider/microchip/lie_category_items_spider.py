from requests import get
from lxml import etree
import logging

from db.company.mysql_client import LieBrand, LieCategory, LieCategoryItems
import re
from unittest import TestCase, main

class LieCategoryItemsSpider(object):
    def __init__(self, brand_id, cat_id, url):
        self.api_url = 'http://www.microchip.com/ParamChartSearch' +\
                '/chart.aspx?branchID=%s'
        brand_name = 'microchip'
        self.url = url
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
        self.brand_id = brand_id
        self.cat_id = cat_id

    def get_lie_category_items(self):
        r = get(self.url, headers=self.headers)
        status_code = r.status_code 
        if status_code == 200:
            r.encoding = 'utf-8'
            html = r.text
            return html
        else:
            return None

    def parse_get_lie_category_items(self, html):
        if not html:
            return

        if self.rule_direct_branchID(html):
            self.parse_branchID_page(html)
            return

        branchID = self.rule_default_grids_branchID(html)
        logging.debug('branchID: %s' % branchID)
        if branchID:
            url = self.api_url % branchID

            r = get(url, headers=self.headers)
            r.encoding = 'utf-8'
            html = r.text
            self.parse_branchID_page(html)
            return
        
        branchID_url = self.rule_new_popular_product(html)
        if branchID_url:
            r = get(branchID_url, headers=self.headers)
            r.encoding = 'utf-8'
            html = r.text
            self.parse_branchID_page(html)
            return

    def parse_branchID_page(self, html):
        tree = etree.HTML(html)
        table_xpath = '//table[@id="ctl00_ctl00_MainContent'+\
                '_PageContent_uc_ComparisonChart1_tblDetail"]'
        table = tree.xpath(table_xpath)
        i = 1
        trs = table[0].xpath('./tr')

        while i < len(trs):
            items_name = trs[i].xpath('./td[1]/a/text()')
            url = trs[i].xpath('./td[2]/a/@href')
            err = 0
            if items_name:
                items_name = items_name[0].encode().decode()
            else:
                items_name = ''
                err += 1
            if url:
                url = url[0].encode().decode()
            else:
                url = ''
                err += 1
            if err == 2:
                continue
            lci = self.new_lie_category_items(items_name, url)
            items_id = LieCategoryItems.\
                    get_items_id_by_items_name(items_name)
            if not items_id:
                LieCategoryItems.addLieCategoryItems(lci)
            i += 1

    def new_lie_category_items(self, items_name, url):           
        lieCategoryItems = LieCategoryItems()
        lieCategoryItems['items_name'] = items_name.lstrip().rstrip()
        lieCategoryItems['url'] = url.lstrip().rstrip()
        lieCategoryItems['brand_id'] = self.brand_id
        lieCategoryItems['cat_id'] = self.cat_id
        return lieCategoryItems

    def rule_default_grids_branchID(self, html):
        match = re.compile(r'DefaultGrid: \d+,')
        result = match.search(html)
        default_grid = None
        if result:
            default_grid  = result.group()
        if not default_grid:
            return None
        else:
            match = re.compile(r'\d+')
            result = match.search(default_grid)
            branchID = result.group()
            return branchID if branchID else None

    def rule_direct_branchID(self, html):
        if 'branchID' in self.url:
            return True
        else:
            return False

    def rule_new_popular_product(self, html):
        match = re.compile(r'href=.+><span>New/Popular Products')
        m = match.search(html)
        if m:
            result = m.group()
            result = result[6:-28]
            return ''.join(['http://www.microchip.com', result])
        else:    
            return None

if __name__ == '__main__':
    url = 'http://www.microchip.com/design-centers/'+\
            'capacitive-touch-sensing/1d-touch'
    lcis = LieCategoryItemsSpider(14,1125,url)
    html = lcis.get_lie_category_items()
    lcis.parse_get_lie_category_items(html)
