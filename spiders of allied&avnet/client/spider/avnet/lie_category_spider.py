from lxml import etree
import requests
from client.spider.base import Spider
import logging

class LieCategorySpider(Spider):
    def __init__(self):
        Spider.__init__(self)
        self.url = 'https://www.avnet.com/shop/AllProducts?countryId=apac&deflangId=-1' \
      '&catalogId=10001&langId=-7&storeId=715839038'
        self.headers = {"User-Agent":"Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0)"}

    def get_all_categories(self):
        try:
            r = requests.get(self.url,headers=self.headers, timeout=10)
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
        et = etree.HTML(html)
        result = []
        uls=et.xpath('//div[@class="ap_div_count ap_div_bg_color"]/ul')
        for i in uls:
            t = i.xpath("./li/a/text()")
            p_name=str(t)[2:-2]
            if p_name:
                #没有下一级分类了
                link = i.xpath("./li/a/@href")
                url = str(link)[2:-2]
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
                result.append(lc_0)
            else:
                pass
            if not t:
                # 还有下一级分类的情况
                t = i.xpath("./li/text()")
                p_name=str(t).split("\\")[0][2:]
                lc_0 = {
                    'cat_name': p_name,
                    'keywords': p_name,
                    'cat_desc': '',
                    'parent_id': 0,
                    'sort_order': '50',
                    'is_show': '1',
                    'url': '',
                    'ext_fields': '',
                    'recom_attr': '',
                    'islast': '',
                    'level': 0,
                    'page_count': 1,
                    'sub_categoreis': [],
                }
                sublis = i.xpath('./li/ul/li')
                for subli in sublis:
                    sub = subli.xpath("./a/text()")
                    link = subli.xpath("./a/@href")
                    name = (str(sub)[2:-2])
                    url = (str(link)[2:-2])
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
    result = lc.parse_get_all_categories(html)
    import pprint
    pprint.pprint(result)
