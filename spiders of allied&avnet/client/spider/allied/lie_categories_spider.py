from lxml import etree
import requests
from client.spider.base import Spider
import logging

class LieCategorySpider(Spider):
    def __init__(self):
        Spider.__init__(self)
        self.url = 'http://www.alliedelec.com'
        self.headers = {"User-Agent":"Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0)"}

    def get_all_categories(self):
        try:
            r = requests.get(self.url,headers=self.headers, timeout=30)
            if r.status_code == 200:
                r.encoding = 'utf-8'
                return r.text
            else:
                r = requests.get(self.url, timeout=30, proxies=self.proxies())
                if r.status_code == 200:
                    r.encoding = 'utf-8'
                    return r.text
                return None
        except Exception as e:
            print('10秒连接超时，切换代理IP')
            r = requests.get(self.url, timeout=30, proxies=self.proxies())
            if r.status_code == 200:
                r.encoding = 'utf-8'
                return r.text
            return None


    def parse_get_all_categories(self, html):
        if html is None:
            return
        result=[]
        et = etree.HTML(html)
        cats=et.xpath('//span[@class="categoryMenuItem"]')
        for cat in cats:
            p_name=cat.xpath('./a[@class="productHeaderMenuLinks"]/text() ')[0].strip()
            url="http://www.alliedelec.com"+cat.xpath('./a[@class="productHeaderMenuLinks"]/@href ')[0]
            lc_0 = {
                'cat_name': p_name,
                'keywords': p_name,
                'cat_desc': '',
                'parent_id': 0,
                'sort_order': '50',
                'is_show': '1',
                'url': url,
                'ext_fields': '',
                'recom_attr': '',
                'islast': '',
                'level': 0,
                'page_count': 1,
                'sub_categoreis': [],
            }
            subs=cat.xpath('./ul/li/span[@class="subCategoryMenuItem"]')
            for sub in subs:
                name=sub.xpath('./a[@class="productHeaderMenuLinks"]/text() ')[0].strip()
                url="http://www.alliedelec.com"+sub.xpath('./a[@class="productHeaderMenuLinks"]/@href ')[0]
                lc_1 = {
                    'cat_name': name,
                    'keywords': name,
                    'cat_desc': '',
                    'parent_id': p_name,
                    'sort_order': '50',
                    'is_show': '1',
                    'url': url,
                    'ext_fields': '',
                    'recom_attr': '',
                    'islast': '',
                    'level': 1,
                    'page_count': 1,
                }
                lc_0["sub_categoreis"].append(lc_1)
            result.append(lc_0)
        return result


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    lc = LieCategorySpider()
    html = lc.get_all_categories()
    result=lc.parse_get_all_categories(html)
    import pprint
    pprint.pprint(result)