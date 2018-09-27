import requests
from lxml import etree

class lie_brand():
    def __init__(self):
        self.header = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36'
                          ' (KHTML, like Gecko) Chrome/57.0.2987.98 Safari/537.36',
            'Referer': 'http://www.mouser.hk/Electronic-Components/?',
        }

    def get_brands(self):
        url = "http://www.mouser.hk/Electronic-Components/?"
        try:
            r = requests.get(url, headers=self.header,timeout = 30, proxies={'http:': '103.22.173.230:80'})
            r.encoding = 'utf-8'
            content = r.text
            print(content)
            tree = etree.HTML(content)
            print(tree)
            names = tree.xpath('//a[@class="SearchResultsTopLevelCategory"]/text()')
            print('名字:', names)
            print(names)
            links = tree.xpath('//a[@class="SearchResultsTopLevelCategory"]/@href')
            print(links)
        except:
            print("fail to get html")

if __name__ == '__main__':
    obj = lie_brand()
    obj.get_brands()
