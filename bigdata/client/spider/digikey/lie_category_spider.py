from lxml import etree
from requests import get
import logging
from unittest import TestCase, main
import pprint
from client.spider.base import Spider

class LieCategorySpider(Spider):
    def __init__(self):
        Spider.__init__(self)
        self.url = 'http://www.digikey.cn/products/zh'
        self.headers = {
            'Host': 'www.digikey.cn',
            #'Connection': 'keep-alive',
            'Cache-Control': 'max-age=0',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64)'+\
                    ' AppleWebKit/537.36 (KHTML, like Gecko) '+\
                    'Chrome/56.0.2924.87 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/'+\
                    'xml;q=0.9,image/webp,*/*;q=0.8',
            'Referer': 'http://www.digikey.cn/products/zh',
            'Accept-Encoding': 'gzip, deflate, sdch',
            'Accept-Language': 'zh-CN,zh;q=0.8',
        }
        self.product_detail_url = 'http://www.digikey.cn'

    def products(self):
        try:
            r = get(self.url, headers=self.headers, timeout=10)
            status_code = r.status_code
            if status_code == 200:
                r.encoding = 'utf-8'
                return r.text
            else:
                r = get(self.url, headers=self.headers, timeout=30, 
                        proxies=self.proxies())
                if r.status_code == 200:
                    r.encoding = 'utf-8'
                    return r.text
                else:
                    return None
        except Exception as e:
            print('10秒连接超时，切换代理IP')
            r = get(self.url, headers=self.headers, timeout=30, 
                        proxies=self.proxies())
            if r.status_code == 200:
                r.encoding = 'utf-8'
                return r.text
            else:
                return None

    def parse_products(self, html):
        if not html:
            return

        categories = list()

        tree = etree.HTML(html)
        div = tree.xpath('//div[@id="productIndexList"]')[0]
        logging.debug(div)
        # 获取总元素个数，然后，循环，由于这里是每3个循环一个大分类
        elems = div.xpath('./*')
        count = len(elems)
        i = 0 

        while i < count:
            # 大分类的名称
            h2_a_text = elems[i].xpath('./a/text()')[0].encode().decode()
            h2_a_href = elems[i].xpath('./a/@href')[0].encode().decode()
            logging.debug(h2_a_text)
            logging.debug(h2_a_href)
            lc_0 = self.package_new_lieCategory(
                    cat_name = h2_a_text,
                    keywords = h2_a_text, 
                    cat_desc = h2_a_text, 
                    parent_id = 0, 
                    sort_order = 50,
                    is_show = 1,
                    url = h2_a_href,
                    ext_fields = '',
                    recom_attr = '',
                    islast = 0,
                    level = 0
                    )

            lc_0['sub_categories'] = list()

            ad = 3
            ul = None
            if h2_a_text in ['未分类', 'Zspecial']:
                ul = elems[i+1]
                ad = 2
            else:
                ul = elems[i+2]
            for li in ul.xpath('./li'):
                a_text =li.xpath('./a/text()')[0].encode().decode()
                a_href =li.xpath('./a/@href')[0].encode().decode()
                logging.info(a_text)
                logging.info(a_href)
                lc_1 = self.package_new_lieCategory(
                    cat_name = a_text,
                    keywords = a_text, 
                    cat_desc = a_text, 
                    parent_id = lc_0['cat_name'], 
                    sort_order = 50,
                    is_show = 1,
                    url = a_href,
                    ext_fields = '',
                    recom_attr = '',
                    islast = 0,
                    level = 1
                    )
                lc_0['sub_categories'].append(lc_1)
            categories.append(lc_0)

            i += ad
        return categories

    def package_new_lieCategory(self, cat_name, keywords, cat_desc, parent_id,
            sort_order, is_show, url, ext_fields, recom_attr, islast, level):
        lc = dict()
        lc['cat_name'] = cat_name
        lc['keywords'] = keywords
        lc['cat_desc'] = cat_desc
        lc['parent_id'] = parent_id
        lc['sort_order'] = sort_order
        lc['is_show'] = is_show
        lc['url'] = url
        lc['ext_fields'] = ext_fields
        lc['recom_attr'] = recom_attr
        lc['islast'] = islast
        lc['level'] = level
        lc['page_count'] = 1

        lc['url'] = ''.join([self.product_detail_url, lc['url']])

        return lc

class Test(TestCase):
    def setUp(self):
        self.lcs = LieCategorySpider()

    def tearDown(self):
        del self.lcs

    def test_parse_products(self):
        html = self.lcs.products()
        categories = self.lcs.parse_products(html)
        pprint.pprint(categories)

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    main()
