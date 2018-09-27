from lxml import etree
import requests
import pika
import json
import threading
import traceback
import time

lock = threading.Lock()

from client.spider.base import Spider


class LieGoodsPagnationSpider(Spider):
    def __init__(self, cat_id,url, ch, rk):
        Spider.__init__(self)
        self.rk = rk
        self.ch = ch
        self.url=url
        self.cat_id=cat_id
        self.headers = {
            'Accept':'application/json, text/javascript, */*; q=0.01',
            'Referer':url,
            'User-Agent':'Mozilla/5.0 (Windows NT 6.1; Win64; x64)'+\
                    'AppleWebKit/537.36 (KHTML, like Gecko)'+\
                    'Chrome/56.0.2924.87 Safari/537.36',
            'X-Requested-With':'XMLHttpRequest',
        }

    def get_total_pages(self, proxy_queue):
        global lock
        print('本地IP使用次数:', Spider.LOCAL_IP_USE_COUNT)
        print('代理IP使用次数:', Spider.PROXY_IP_USE_COUNT)
        if Spider.LOCAL_IP_USE_COUNT <= 4:
            with lock:
                Spider.LOCAL_IP_USE_COUNT += 1 
            if Spider.LOCAL_IP_USE_COUNT >= 4:
                with lock:
                    Spider.PROXY_IP_USE_COUNT = 0
            return self.get_no_proxies(self.url, headers=self.headers,timeout=30)
        if Spider.PROXY_IP_USE_COUNT <= 4:
            with lock:
                Spider.PROXY_IP_USE_COUNT += 1
            if Spider.PROXY_IP_USE_COUNT >= 4:
                with lock:
                    Spider.LOCAL_IP_USE_COUNT = 0
            return self.get_use_proxies(self.url, self.headers,
                    50, self.ch, proxy_queue)

    def parse_get_total_pages(self, html):
        if not html:
            return
        et = etree.HTML(html)
        pageid = str(et.xpath('//meta[@name="pageId"]/@content'))[2:-2]
        print(pageid)

        link = str('https://www.avnet.com/search/resources/store/715839035/productview/byCategory/'+pageid+'?searchType=100&profileName=Avn_findProductsByCategory_Summary&searchSource=Q&storeId=715839035&catalogId=10001&langId=-1&responseFormat=json&pageSize=20&pageNumber=1&_wcf.search.internal.boostquery=price_USD:{0.00001+TO+*}^499999.0+inStock:%22true%22^9000.0+topSellerFlag:%22Yes%22^0.085+newProductFlag:%22Yes%22^0.080+packageTypeCode:%22BKN%22^0.075&wt=json')

        content = self.get(link)[:100]
        a = content.split(':')[1]
        resultsReturned = int(a.split(',')[0])

        print('总个数:', resultsReturned)

        total_page = resultsReturned // 100
        if resultsReturned % 100 != 0:
            total_page += 1
        body = str({"1": {'cat_id': self.cat_id, 'page_count': total_page,
            'pageid': pageid}})

        print('总页数', total_page)
        self.ch.basic_publish(exchange='', routing_key=self.rk,
                properties = pika.BasicProperties(delivery_mode=2),
                body=body)

    def pagnation(self,pageid, page, proxy_queue):
        if page==1:
            link = ('https://www.avnet.com/search/resources/store/715839035/productview/byCategory/'+pageid+'?searchType=100&profileName=Avn_findProductsByCategory_Summary&searchSource=Q&storeId=715839035&catalogId=10001&langId=-1&responseFormat=json&pageSize=100&pageNumber=1&_wcf.search.internal.boostquery=price_USD:{0.00001+TO+*}^499999.0+inStock:%22true%22^9000.0+topSellerFlag:%22Yes%22^0.085+newProductFlag:%22Yes%22^0.080+packageTypeCode:%22BKN%22^0.075&wt=json')
        else:
            link = ('https://www.avnet.com/search/resources/store/715839035/productview/byCategory/'+pageid+'?searchType=100&profileName=Avn_findProductsByCategory_Summary&searchSource=Q&storeId=715839035&catalogId=10001&langId=-1&responseFormat=json&pageSize=100&pageNumber='+str(page)+'&_wcf.search.internal.boostquery=price_USD:{0.00001+TO+*}^499999.0+inStock:%22true%22^9000.0+topSellerFlag:%22Yes%22^0.085+newProductFlag:%22Yes%22^0.080+packageTypeCode:%22BKN%22^0.075&showMore=true&intentSearchTerm=*&searchTerm=*&wt=json')
        self.link = link

        global lock       
        if Spider.LOCAL_IP_USE_COUNT <= 3:
            with lock:
                Spider.LOCAL_IP_USE_COUNT += 1
            if Spider.LOCAL_IP_USE_COUNT >= 3:
                Spider.PROXY_IP_USE_COUNT = 0
            return self.get_no_proxies(link, headers=self.headers, timeout=50)
        if Spider.PROXY_IP_USE_COUNT <= 3:
            with lock:
                Spider.PROXY_IP_USE_COUNT += 1
            if Spider.PROXY_IP_USE_COUNT >= 3:
                Spider.LOCAL_IP_USE_COUNT = 0
            return self.get_use_proxies(link, self.headers, 50, self.ch, 
                    proxy_queue)

    def parse_pagnation(self,html):
        if not html:
            return
        #得到json之后进行分析，得到数据并且放入
        datas = ''
        try:
            datas = html.split('{"catalogEntryTypeCode":"ItemBean",')[1:]
            datas[-1] = str(datas[-1])[:-1]
        except Exception as e:
            '''
            with open('F:解析异常.html', 'w') as f:
                f.write(self.link + '\n')
                f.write(html)
            input('输出 调试信息 ')
            '''
            return

        for k in range(len(datas)):
            formalised = str('{"catalogEntryTypeCode":"ItemBean",' + datas[k])[:-1]
            dicpt = json.loads(formalised)
            try:
                goods_name = dicpt['mfPartNumber_ntk']
            except:
                goods_name = ''
            try:
                goods_sn = dicpt['uniqueID']
            except:
                goods_sn = ''
            try:
                goods_desc = dicpt['shortDescription']
            except:
                goods_desc = ''
            try:
                goods_thumb = dicpt['avn_thumbnail']
            except:
                goods_thumb = ''
            try:
                site_url = str("https://products.avnet.com/shop/zh-CN/asia/" + dicpt['avn_pdp_seo_path'])
            except:
                site_url = ''
            self.add_goods(goods_name, goods_sn,goods_desc, goods_thumb,site_url,self.cat_id)

    def add_goods(self,goods_name, goods_sn,goods_desc, goods_thumb,site_url,cat_id):
        #放入队列/MYSQL
        lg = dict()
        lg['pdf_url'] = ''
        lg['goods_thumb'] = goods_thumb
        lg['site_url'] = site_url

        lg['cat_id'] = cat_id
        lg['goods_sn'] = goods_name+"&"+goods_sn
        lg['goods_name'] = goods_name
        lg['provider_name'] = ''
        lg['goods_number'] = ''
        lg['min_buynum'] = ''
        lg['goods_brief'] = ''
        lg['goods_desc'] = goods_desc
        lg['goods_img'] = ''
        lg['series'] = ''
        lg['warehouse'] = ''
        lg['Encap'] = ''
        lg['Package'] = ''
        lg['HDT'] = ''
        lg['CDT'] = ''
        lg['goods_name_style'] = '+'

        body = str({'1': lg})
        with lock:
            self.ch.basic_publish(exchange='',
                    routing_key=self.rk,
                    properties=pika.BasicProperties(
                        delivery_mode = 2),
                    body=body)
        print('Sent', body)

    def get(self,url):
        #从网址中抽出网页内容
        return self.get_no_proxies(url, headers=self.headers, timeout=30)
        
if __name__ == '__main__':
    from client.recv_cron.avnet import recv_pagnation
    conn = recv_pagnation.get_rb_conn()
    ch = conn.channel()
    qn = 'avnet_store_pagnation'
    ch.queue_declare(queue=qn)
    """从之前保存的分类得到每个搭配（cat_id和url，比如无线和GPS模块，
    https://www.avnet.com/shop/apac/zh-CN/c/%E6%97%A0%E7%BA%BF%E5%92%8Cgps%E6%A8%A1%E5%9D%97--7/zigbee--7/。
    注意有二级分类的一级分类url为空，所以这里要做一个判断，有下级分类的跳过，之后）
    for each cat_id,url（不为空）:
        ..."""
    lgps = LieGoodsPagnationSpider(ch, qn,"无线和GPS模块",
                                   "https://www.avnet.com/shop/apac/zh-CN/c/%E6%97%A0%E7%BA%BF%E5%92%8Cgps%E6%A8%A1%E5%9D%97--7/zigbee--7/")
    html=lgps.get_total_pages()
    pageid=lgps.parse_get_total_pages(html)

    html=lgps.pagnation(pageid,1)
    lgps.parse_pagnation(html)



