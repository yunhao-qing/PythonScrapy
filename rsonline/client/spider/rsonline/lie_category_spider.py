# -*- coding:utf-8 -*-
from lxml import etree
import requests
from client.spider.base import Spider
from selenium import webdriver
import time

class LieCategorySpider(Spider):
    def __init__(self):
        Spider.__init__(self)
        self.url = 'http://china.rs-online.com/web'
        self.headers = {
            'User-Agent': 'Mozilla/4.0 (compatible; MSIE 6.0;'
                          'Windows NT 5.2; SV1; .NET CLR 1.1.4322)',
        }

    def get_cat1_page(self,url):
        print('正在访问cat1页面')
        trycount = 0
        while (trycount < 5):
            try:
                r = requests.get(url, headers=self.headers, timeout=1000)
                r.encoding = 'utf-8'
                html = r.content
                return html
            except:
                trycount += 1
        print("失败了", url)


    def get_all_categories(self):
        driver = webdriver.Chrome()
        driver.get(self.url)
        html_source = driver.page_source
        driver.quit()
        return html_source

    def parse_get_all_categories(self, html):
        result=[]
        if html is None:
            return
        et=etree.HTML(html)
        ul=et.xpath('//ul[@class ="verticalMenu hideVerticalMenu"]')[0]
        lis=ul.xpath('./li[@class="verticalMenuOption"]')
        for li in lis:
            lc_0_name = str(li.xpath("./a/text()")[0]).strip()
            print("0"+lc_0_name)
            lc_0_url = "http://china.rs-online.com"+str(li.xpath("./a/@href")[0]).strip()
            lc_0 = {
                'cat_name': lc_0_name,
                'keywords': lc_0_name,
                'cat_desc': '',
                'parent_id': 0,
                'sort_order': '50',
                'is_show': '1',
                'url': lc_0_url,
                'ext_fields': '',
                'recom_attr': '',
                'islast': 0,
                'level': 0,
                'page_count': 1,
                'sub_categories': [],
            }
            subs = li.xpath('./div/ul/li')
            for sub in subs:
                lc_1_name = str(sub.xpath("./a/text()")[0]).strip()
                lc_1_url ="http://china.rs-online.com"+str(sub.xpath("./a/@href")[0]).strip()
                print("1"+lc_1_name)
                lc_1 = {
                    'cat_name': lc_1_name,
                    'keywords': lc_1_name,
                    'cat_desc': '',
                    'parent_id': lc_0_name,
                    'sort_order': '50',
                    'is_show': '1',
                    'url': lc_1_url,
                    'ext_fields': '',
                    'recom_attr': '',
                    'islast': 0,
                    'level': 1,
                    'page_count': 1,
                    'sub_categories': [],
                }
                try:
                    html=self.get_cat1_page(lc_1_url)
                    et=etree.HTML(html)
                    lasts=et.xpath("//ul[@class='brcategories']/li/div/a")
                    if lasts:
                        for last in lasts:
                            lc_2_name=str(last.xpath("./text()")[0]).strip()
                            print("2"+lc_2_name)
                            lc_2_url = str(last.xpath("./@href")[0]).strip()
                            lc_2 = {
                                'cat_name': lc_2_name,
                                'keywords': lc_2_name,
                                'cat_desc': '',
                                'parent_id': lc_1_name,
                                'sort_order': '50',
                                'is_show': '1',
                                'url': lc_2_url,
                                'ext_fields': '',
                                'recom_attr': '',
                                'islast': 1,
                                'level': 1,
                                'page_count': 1,
                                'sub_categories': [],
                            }
                            lc_1["sub_categories"].append(lc_2)
                    else:
                        lc_1["islast"] = 1
                except Exception as e:
                    print(e)
                    print("失败："+lc_1_url)
                lc_0["sub_categories"].append(lc_1)
            result.append(lc_0)
        return result

if __name__ == '__main__':

    lc = LieCategorySpider()
    html = lc.get_all_categories()
    categories = lc.parse_get_all_categories(html)
    import pprint
    pprint.pprint(categories)
