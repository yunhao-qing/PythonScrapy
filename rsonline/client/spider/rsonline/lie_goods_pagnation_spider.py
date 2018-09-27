from lxml import etree
import pika
import threading
import requests
import time

lock = threading.Lock()

from client.spider.base import Spider


class LieGoodsPagnationSpider(Spider):
    def __init__(self, cat_id, url, ch, rk):
        Spider.__init__(self)
        self.cat_id = cat_id
        self.ch = ch
        self.rk = rk
        self.url = url
        self.headers = {
            'User-Agent': 'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.2; SV1; .NET CLR 1.1.4322)',
        }
        self.new_headers = {
            'User-Agent': 'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.2; SV1; .NET CLR 1.1.4322)',
            'Cookie': 'JSESSIONID=t2-hC3zftY8KIDHVgnnaJ6cQ.023; firsttimevisitor=N;'
                      'viewType=List; AMCV_CB3F58CC558AC9FB7F000101%40AdobeOrg=1999'
                      '109931%7CMCMID%7C38059280987425463468757872535808374461%7CMCA'
                      'ID%7CNONE%7CMCAAMLH-1493713394%7C11%7CMCAAMB-1493713394%7Chmk_L'
                      'q6TPIBMW925SPhw3Q%7CMCCIDH%7C-265859109; confirmitjs_msgshown=su'
                      'rveyshown; ak_bmsc=BA67FB87643836310F1D838DECABBF5E3B27427BB2150'
                      '0004EB402594C6AAD23~plPevizcvyrxGklqmXdTCILAYVsRFXsiIuX+ZGbE4NVkL'
                      '4DmIvZ5pfMZL9SqlSSl1PUNpiPiws1zOwx5JhUkYkU2cvDsbsRUpG5AQ+K/nBXKub'
                      'GQhaBuwJJoKL0SIvGau8GerJNav/dNtLGGZwd6/Qw4+/Q9W5kAF94PRUl1v1PUYRI'
                      'poOwfuwpRYtTwpUc8q1QI4sc4yZj/KoLGGdccr2bA==; mbox=PC#149310857848'
                      '7-956765.24_5#1501126791|session#1493349435521-948709#1493352651|c'
                      'heck#true#1493350851; Hm_lvt_d330746eb4f8a468d0355b2818021138=14931'
                      '08586,1493109267,1493110551,1493349436; Hm_lpvt_d330746eb4f8a468d03'
                      '55b2818021138=1493350791; s_cc=true; RT="sl=5&ss=1493349433223&tt=18'
                      '569&obo=0&sh=1493350792897%3D5%3A0%3A18569%2C1493350789102%3D4%3A0%'
                      '3A15331%2C1493350785011%3D3%3A0%3A13717%2C1493350775610%3D2%3A0%3A58'
                      '38%2C1493349437259%3D1%3A0%3A4033&dm=rs-online.com&si=70b6856a-92ec-'
                      '4c90-a364-bc8535379792&bcn=%2F%2F36f1082f.mpstat.us%2F&ld=14933507928'
                      '97&nu=http%3A%2F%2Fchina.rs-online.com%2Fweb%2Fc%2Fpower-supplies-tra'
                      'nsformers%2Ftransformers%2Fdin-rail-panel-mount-transformers%2F&cl=14'
                      '93350796309"; s_sq=rscomponentsprod%3D%2526pid%253Dhttp%25253A%25252'
                      'F%25252Fchina.rs-online.com%25252Fweb%25252Fc%25252Fpower-supplie'
                      's-transformers%25252Ftransformers%25252Fdin-rail-panel-mount-trans'
                      'formers%25252F%2526oid%253Dhttp%25253A%25252F%25252Fchina.rs-online'
                      '.com%25252Fweb%25252Fc%25252Fpower-supplies-transformers%25252Ftran'
                      'sformers%25252Fdin-rail-panel-mount-trans%2526ot%253DA'}

    def get_total_pages(self):
        url = self.url
        r = requests.get(url, headers=self.headers,timeout=50)
        html = r.text
        return html

    def parse_get_total_pages(self, html):
        if html is None:
            return
        resultsReturned = int(html.split('"search_results":"')[1].split('",')[0])
        total_page = resultsReturned // 20
        if resultsReturned % 20 != 0:
            total_page += 1
        print(self.cat_id, resultsReturned)
        body = str({"1": {'cat_id': self.cat_id, 'page_count': total_page}})

        #print('Sent ', body)
        self.ch.basic_publish(exchange='', routing_key=self.rk,
                              properties=pika.BasicProperties(delivery_mode=2),
                              body=body)

    def pagnation(self, page):
        print('正在访问分页')
        page_url = self.url+"?pn="+str(page)
        trycount=0
        while (trycount<5):
            try:
                r = requests.get(page_url, headers=self.new_headers, timeout=50)
                if r.status_code==200:
                    html = r.content
                    return html
                else:
                    trycount+=1
            except:
                trycount +=1
        print("失败了",page_url)

    def parse_pagnation(self,html):
        print('正在解析分页')
        if not html:
            print('分页解析失败')
            return
        et = etree.HTML(html)
        trs = et.xpath('//tr[@class="resultRow"]')
        divs = et.xpath('//td[@class="partColHeader"]/div[@class="partColContent"]')
        if trs:
            for i in range(len(trs)):
                site_url = trs[i].xpath('./td/div/div/a/@href')[0].strip()
                try:
                    goods_desc = trs[i].xpath('./td/div/div/a/text()')[0].strip()
                except:
                    goods_desc = ""
                partId = divs[i].xpath('./ul/li/a[@class="primarySearchLink"]/text()')[0].strip()
                try:
                    goods_name = divs[i].xpath('./ul/li/span[@class="defaultSearchText"]/text()')[0].strip()
                except:
                    goods_name = partId
                provider_name = divs[i].xpath('./ul/li/a[@class="secondarySearchLink"]/text()')[0].strip()
                numbers = partId.split("-")
                goods_thumb = "http://media.rs-online.com/t_thumb/R" + numbers[0] + numbers[1] + "-01.jpg"
                goods_img = "http://media.rs-online.com/t_large/R" + numbers[0] + numbers[1] + "-01.jpg"

                print('产品名称:', goods_name)
                print('小图片:', goods_thumb)
                print('大图片:', goods_img)
                print('RS 库存编号:', partId)
                print('制造商:', provider_name)
                print('site_url:', site_url)
                print("描述：", goods_desc)
                print("-----------------------------------------")
                self.add_goods(goods_name, goods_thumb, goods_img, partId, provider_name, site_url, goods_desc)
                print('2')
        else:
            trs = et.xpath('//table[@class="listViewTable"]/tr')[1:]
            for tr in trs:
                site_url = tr.xpath('./td/table/tr/td/a/@href')[0].strip()
                try:
                    goods_desc = tr.xpath('./td/table/tr/td/a/@title')[0].strip()
                except:
                    goods_desc = ""
                partId = tr.xpath('./td/a/text()')[0].strip()
                try:
                    goods_name = tr.xpath('./td/div[@class="brandPartNoDiv"]/a/text()')[0].strip()
                except:
                    goods_name = partId
                if goods_name == "":
                    goods_name = partId
                provider_name = tr.xpath('./td/div[@class="brandPartNoDiv"]/text()')[0].strip()
                numbers = partId.split("-")
                goods_thumb = "http://media.rs-online.com/t_thumb/R" + numbers[0] + numbers[1] + "-01.jpg"
                goods_img = "http://media.rs-online.com/t_large/R" + numbers[0] + numbers[1] + "-01.jpg"

                print('产品名称:', goods_name)
                print('小图片:', goods_thumb)
                print('大图片:', goods_img)
                print('RS 库存编号:', partId)
                print('制造商:', provider_name)
                print('site_url:', site_url)
                print("描述：", goods_desc)
                print("-----------------------------------------")
                self.add_goods(goods_name, goods_thumb, goods_img, partId, provider_name, site_url, goods_desc)
                print('2')

    def add_goods(self, goods_name, goods_thumb, goods_img,partId, provider_name, site_url,goods_desc):
        lg = dict()
        lg['pdf_url'] = ''
        lg['goods_thumb'] = goods_thumb
        lg['site_url'] = site_url

        lg['cat_id'] = self.cat_id
        lg['goods_sn'] = goods_name + '€€' + str(partId)
        lg['goods_name'] = goods_name
        lg['provider_name'] = provider_name
        lg['goods_number'] = ''
        lg['min_buynum'] = 1
        lg['goods_brief'] = ''
        lg['goods_desc'] = goods_desc
        lg['goods_img'] = goods_img
        lg['series'] = ''
        lg['warehouse'] = ''
        lg['Encap'] = ''
        lg['Package'] = ''
        lg['HDT'] = ''
        lg['CDT'] = ''
        lg['goods_name_style'] = '+'
        lg['is_check'] = 0

        body = str({'1': lg})
        with lock:
            self.ch.basic_publish(exchange='', routing_key=self.rk,
                                  body=body)
        print('Sent', body)



if __name__ == '__main__':
    from client.recv_cron.rsonline import recv_pagnation

    conn = recv_pagnation.get_rb_conn()
    ch = conn.channel()
    qn = 'rsonline_store_pagnation'
    ch.queue_declare(queue=qn)

    lgps = LieGoodsPagnationSpider(64,
                                   "http://china.rs-online.com/web/c/"
                                   "semiconductors/sensor-ics/differential-pressure-sensor-ics/",
                                   ch, qn)

    html = lgps.get_total_pages()
    lgps.parse_get_total_pages(html)

    html = lgps.pagnation(1)
    lgps.parse_pagnation(html)
