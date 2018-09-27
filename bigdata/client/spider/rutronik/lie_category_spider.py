import requests as req
from lxml import etree
from client.spider.base import Spider
import re
import pprint

class LieCategorySpider(Spider):
    def __init__(self):
        self.url = 'https://www.rutronik24.com/?_ga=1.179757287.27243758.1491879245#'
        self.headers = {
            'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Encoding':'gzip, deflate, sdch, br',
            'Accept-Language':'zh-CN,zh;q=0.8',
            'Cache-Control':'max-age=0',
            'Connection':'keep-alive',
            'Cookie':'PHPSESSID=eo7u54vos35iadvqcqvfl39l85; _ga=GA1.2.1082501521.1491879481; _gat=1; emos_jcsid=AVta8lOsKDlatARS3joDMGhyJAypKQWu:1:AVta8lOr4LQkKoS8dHqiPtEGDhJcsv7o:1491879482283; emos_jcvid=AVta8lOsKDlatARS3joDMGhyJAypKQWu:1:AVta8lOsKDlatARS3joDMGhyJAypKQWu:1491879482283:0:true:1; _gali=form_lang; RUTOCLANGUAGE=cn; RUTCURRENCY=EUR; R24REF=a%3A4%3A%7Bs%3A3%3A%22uid%22%3Bs%3A32%3A%2289c695f52b7f7d35452ece9819071bcd%22%3Bs%3A4%3A%22time%22%3Bi%3A1492484292%3Bs%3A7%3A%22referer%22%3BN%3Bs%3A3%3A%22uri%22%3Bs%3A0%3A%22%22%3B%7D',
            'Host':'www.rutronik24.com',
            'Referer':'https://www.rutronik24.com/',
            'Upgrade-Insecure-Requests':'1',
            'User-Agent':'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537',
        }

    def get_all_categories(self):
        r = req.get(self.url, headers=self.headers, timeout=30)
        r.encoding = 'utf-8'
        return r.text if r.status_code == 200 else None

    def parse_get_all_categories(self, html):
        if not html:
            return
        tree = etree.HTML(html)
        div = tree.xpath('//div[@id="nestedAccordion"]')
        div = div[0] if len(div) != 0 else None
        if div is None:
            print('根元素获取失败')
            return

        categories = []
        sbs = div.xpath('./*')[4:]
        i = 0    
        sig = 0
        sub_sig = 0
        lc = dict()
        lc_0 = dict()
        lc_1 = dict()
        while i < len(sbs):
            try:
                # 1
                if sbs[i].xpath('./@class')[0].startswith('bereich'):
                    lc = dict()
                    lc_0 = dict()
                    lc_1 = dict()

                    sig = 1
                    lc['cat_name'] = sbs[i].xpath('./text()')[0]
                    lc['level'] = 0
                    lc['parent_id'] = 0
                    lc['url'] = ''
                    lc['sub_categories'] = []
                    categories.append(lc)
                    i += 1
                    continue 
            except Exception as e:
                pass
            try:
                # 2
                if sig == 1:
                    tmp = ''.join(sbs[i].xpath('./text()'))
                    if  tmp != '':
                        lc_0['cat_name'] = tmp
                        lc_0['level'] = 1
                        lc_0['parent_id'] = lc['cat_name']
                        lc_0['url'] = ''
                        lc['sub_categories'].append(lc_0)
                        sub_sig = 1
                        sig = 0
                    i += 1
                    continue 
            except Exception as e:
                pass
            try:
                # 3
                if sub_sig == 1:
                    for a in sbs[i].xpath('./a'):
                        lc_1['cat_name'] = sbs[i].xpath('./text()')[0]
                        lc_1['url'] = sbs[i].xpath('./@href')[0]
                        lc_1['level'] = 2
                        lc_1['parent_id'] = lc_0['cat_name']
                        lc_1['sub_categories'] = []
                    sub_sig = 0
                    sig = 1
                    i += 1
                    continue 

            except Exception as e:
                pass
            i += 1

        pprint.pprint(categories)

if __name__ == '__main__':
    import logging
    logging.basicConfig(level=logging.DEBUG)
    lcs = LieCategorySpider()
    html = lcs.get_all_categories()
    cgs = lcs.parse_get_all_categories(html)
