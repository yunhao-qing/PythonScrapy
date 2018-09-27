from requests import get
from lxml import etree
import logging
import time
from threading import Lock
import pika
from client.spider.base import Spider

lock = Lock()

class LieGoodsSpider(Spider):
    '''
    PS. 这个类调用有两种情况
    1. 分页成功的时候，默认会增加goods简略的信息到数据库，然后这里就这样玩.
    >>lgs = LieGoodsSpider(cat_id, goods_id, goods_sn, url, pdf_url)

    2. 分页失败，小分类点进去就是详情这种情况
    >>lgs = LieGoodsSpider(cat_id, goods_id=None, goods_sn=None, url, pdf_url=None)
    '''
    def __init__(self, cat_id, goods_id, goods_sn, url, pdf_url, ch, routingkey,
            is_first):
        Spider.__init__(self)
        self.cat_id = cat_id
        self.goods_id = goods_id
        self.goods_sn = goods_sn
        self.url = url
        self.pdf_url = pdf_url
        self.headers = {
            'Host': 'www.digikey.cn',
            'Cache-Control': 'max-age=0',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) '+\
                    'AppleWebKit/537.36 (KHTML, like Gecko) '+\
                    'Chrome/56.0.2924.87 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml'+\
                    ';q=0.9,image/webp,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate, sdch',
            'Accept-Language': 'zh-CN,zh;q=0.8',
        }
        self.ch = ch
        self.routingkey = routingkey
        self.is_first = is_first

    def goods(self, proxy_queue):   
        return self.get_no_proxies(self.url, headers=self.headers, timeout=30)

    def parse_goods(self, html):
        if not html:
            return -1
        try:
            sig = self.rule_img_left(html)
            if sig:
                return
            logging.debug('第一种规则解析失败了')
        except BaseException as be:
            raise be

    def fz_goods_detail(self, goods_name, brand_name,
                    desc, pn, stock, tiered):
        dgk = dict()
        dgk['goods_id'] = self.goods_id
        dgk['goods_name'] = goods_name
        dgk['goods_sn'] = self.goods_sn
        dgk['brand_name'] = brand_name
        dgk['desc'] = desc
        dgk['docurl'] = self.pdf_url
        dgk['pn'] = pn
        dgk['stock'] = stock
        dgk['tiered'] = tiered
        dgk['increment'] = 1
        dgk['time']  = int(time.time())
        dgk['url'] = self.url
        return dgk

    def rule_img_left(self, html):
        if not html:
            return
        tree = etree.HTML(html)
        pdb_content = tree.xpath('//*[@id="pdp_content"]')
        pdb_content = pdb_content[0] if pdb_content else None

        # product-top-section
        # **********************************************************************
        pts = pdb_content.xpath('//div[@class="product-top-section"]')
        pts = pts[0] if pts else None
        # 解析图片
        pimg = pdb_content.xpath('//div[@id="product-photo-wrapper"]/a/img/@src')
        pimg = ''.join(pimg).strip() if len(pimg)!=0 else ''
        logging.debug('产品图片链接: %s\n' % pimg)
        # 产品概览
        pdt = pdb_content.xpath('//table[@id="product-details"]')[0]
        trs = pdt.xpath('./tr')

        goods_name = ''#
        goods_name_style = ''
        kc = ''
        zzs = ''
        zzs_url = ''
        for tr in trs:
            th = ''.join(tr.xpath('./th')[0].xpath('./text()')).strip()
            td = ''
            if 'Digi-Key 零件编号' == th:
                # 如果Digi-Key 零件编号
                td = ''.join(tr.xpath('./td')[0].xpath('./text()')).strip()
                goods_name_style = td
            elif '现有数量' == th: 
                td = ''.join(tr.xpath('./td')[0].\
                        xpath('./span[@id="dkQty"]/text()'))
                kc = td
            elif '制造商' == th:
                td = ''.join(tr.xpath('./td')[0].\
                        xpath('./h2/span/a/span/text()')).strip()
                zzs = td
                td = ''.join(tr.xpath('./td')[0].\
                        xpath('./h2/span/a/@href')).strip()
                zzs_url = 'http://www.digikey.cn' + td
            elif '制造商零件编号' == th:
                td = ''.join(tr.xpath('./td')[0].\
                        xpath('./h1/text()')).strip()
                goods_name = td
            elif '描述' == th:
                td = ''.join(tr.xpath('./td')[0].\
                        xpath('./text()')).strip()
                desc = td

        if kc == '':
            kc = 0
        logging.debug('Digikey零件编号: %s' % goods_name_style)
        logging.debug('库存: %s' % kc)
        logging.debug('制造商: %s' % zzs)
        logging.debug('制造商url: %s' % zzs_url)
        logging.debug('制造商零件编号: %s' % goods_name)
        logging.debug('描述: %s' % desc)
        
        
        # product-dollars
        # **********************************************************************
        logging.debug('解析价格梯度')
        pd = pdb_content.xpath('//table[@id="product-dollars"]')
        pd = pd[0] if pd else None

        tiered = []
        stock = []
        try:
            if pd is None:
                # 价格梯度第一次解析失败
                logging.debug('价格梯度第一次解析失败，'
                              '大哥，可能遇到那种没有图片,没有梯度的数据了')
                '''
                with open('/data/log/bigdata/digikey/那种没有图片梯度的数据.txt', 'a') as f:
                    logstr = dict(
                        time_ = time.ctime(),
                        cat_id=self.cat_id,
                        goods_id=self.goods_id,
                        url=self.url,
                        goods_sn=self.goods_sn
                    )
                    f.write(str(logstr)+'\n')
                '''
                logging.debug('%s\n' % tiered)
            else:
                trs = pd.xpath('./tr')[1:]
                tc = 0
                for tr in trs:
                    tds = tr.xpath('./td')
                    gn = int(tds[0].xpath('./text()')[0].replace(',' ,''))
                    gp = None
                    if tc == 0:
                        gp = tds[1].xpath('./span/text()')[0]
                        stock.append(gn)
                    else:
                        gp = tds[1].xpath('./text()')[0]
                    gp = float(''.join(gp.split(','))) if gp else None
                    tiered.append([gn, gp])
                    tc += 1
                # bug 0 TODO
                logging.debug('stock: %s' % str(stock))
                logging.debug('%s\n' % tiered)

        except Exception as e:
            print(e)
            stock = [0,]
        finally:
            stock.append(kc)

        if self.is_first:
            print('**********************更新mysql**********************')
            # prod-attributes
            # **********************************************************************
            pa = pdb_content.xpath('//div[@class="prod-attributes"]')
            pa = pa[0] if pa else None
            atm = pa.xpath('//table[@id="prod-att-table"]')[0]
            trs = atm.xpath('./tr')[1:]
                
            attrs = dict()
            i = 0
            while i < len(trs):
                if i == 0:
                    # 解析类别
                    ga = trs[i].xpath('./th')[0].xpath('./text()')[0]
                    gv = trs[i].xpath('./td')[0].xpath('./a/text()')[0]
                    tmp = ''.join(trs[i+1].xpath('./td')[0].\
                            xpath('./a/text()')).strip()
                    gv = gv + ', ' + tmp
                    logging.debug('%s: %s' % (ga, gv))
                    attrs[ga] = gv
                    i += 2
                    continue
                if i == 2:
                    ga = ''.join(trs[i].xpath('./th')[0].\
                            xpath('./text()')[0]).strip()
                    gv = ''.join(trs[i].xpath('./td')[0].\
                            xpath('./h3/text()')[0]).strip()
                    logging.debug('%s: %s' % (ga, gv))
                    attrs[ga] = gv
                    i += 1
                    continue
                ga = ''.join(trs[i].xpath('./th')[0].xpath('./text()')[0]).strip()
                gv = ''.join(trs[i].xpath('./td')[0].xpath('./text()')[0]).strip()
                logging.debug('%s: %s' % (ga, gv))
                attrs[ga] = gv
                i += 1
            print(attrs)

            # 增加和更新brand
            lieBrand = dict()
            lieBrand['brand_name'] = zzs.encode().decode()
            lieBrand['site_url'] = zzs_url.encode().decode()

            '''
            r = get(lieBrand['site_url'], headers=self.headers)
            r.encoding = 'utf-8'
            tree1 = etree.HTML(r.text)
            zzs_logo = tree1.xpath(
                    '//*[@id="form1"]/div[4]/div/table/tbody/tr/td[1]')
            if zzs_logo and len(zzs_logo) != 0:
                logging.debug('制造商logo匹配成功')
                zzs_logo = zzs_logo[0].xpath('./a')[0].xpath('./img')[0].\
                        xpath('./@src')[0].encode().decode()
            else:
                logging.debug('制造商logo匹配失败')
                zzs_logo = tree1.xpath(
                        '//*[@id="pagelayout_0_content_2__vendorLink"]/img/@src')
            logging.debug('制造商logo: %s' % zzs_logo)
            lieBrand['brand_logo'] = zzs_logo
            '''
            lieBrand['brand_logo'] = ''
            lieBrand['brand_desc'] = ''
            lieBrand['web_url'] = ''

            body = {
                'lieBrand': lieBrand,
                'attrs': attrs,
                'goods_id': self.goods_id,
                'cat_id': self.cat_id
            }
            body = str({"2": body})
            self.ch.basic_publish(exchange='',
                    routing_key=self.routingkey,
                    properties=pika.BasicProperties(
                        delivery_mode = 2),
                    body=body)
            body = ''

            # 更新goods mysql
            lg = self.update_goods_mysql(goods_name, zzs, pimg, desc, 
                    goods_name_style)
            body = str({"1": lg})
            self.ch.basic_publish(exchange='',
                    routing_key=self.routingkey, 
                    properties=pika.BasicProperties(
                        delivery_mode = 2),
                    body=body)
            body = ''

            # 
            goods_price = []
            for ti in tiered:
                tmp = {'purchases': ti[0], 'price': ti[1]}
                goods_price.append(tmp)
            body = {'goods_price': goods_price, 'goods_id': self.goods_id}
            body = str({"4": body})
            self.ch.basic_publish(exchange='',
                    routing_key=self.routingkey, 
                    properties=pika.BasicProperties(
                        delivery_mode = 2),
                    body=body)
            body = ''

            print('**********************更新mongo**********************')
            dgk = self.fz_goods_detail(goods_name, 
                    zzs.encode().decode(), desc, pn='digikey', 
                    stock=stock, tiered=tiered)
            if '已过时' in html:
                dgk['is_error'] = 1
            if '不再生产' in html:
                dgk['is_error'] = 2

            body = {
                'dgk': dgk,
                'goods_sn': self.goods_sn,
            }
            body = str({"3": body})
            self.ch.basic_publish(exchange='',
                    routing_key=self.routingkey,
                    properties=pika.BasicProperties(
                        delivery_mode = 2),
                    body=body)
            body = ''
        else:
            # 更新mongo
            print('**********************更新mongo**********************')
            dgk = self.fz_goods_detail(goods_name, 
                    zzs.encode().decode(), desc, pn='digikey', 
                    stock=stock, tiered=tiered)

            if '已过时' in html:
                dgk['is_error'] = 1 
            if '不再生产' in html:
                dgk['is_error'] = 2
            body = {
                'dgk': dgk,
                'goods_sn': self.goods_sn,
            }
            body = str({"3": body})
            self.ch.basic_publish(exchange='',
                    routing_key=self.routingkey,
                    properties=pika.BasicProperties(
                        delivery_mode = 2),
                    body=body)
            body = ''
        return True

    def update_goods_mysql(self, goods_name, zzs, goods_img, goods_desc,
            goods_name_style):
        lg = dict()
        lg['goods_sn'] = self.goods_sn
        lg['goods_name'] = goods_name
        lg['provider_name'] = zzs
        lg['goods_img'] = goods_img
        lg['goods_desc'] = goods_desc
        lg['goods_name_style'] = goods_name_style
        lg['goods_id'] = self.goods_id
        return lg

if __name__ == '__main__':
    from client.settings import rabbitmq_server
    user = rabbitmq_server['user']
    password = rabbitmq_server['password']
    host = rabbitmq_server['host']
    credentials = pika.PlainCredentials(user, password)
    connection = pika.BlockingConnection(pika.ConnectionParameters(
            host=host, credentials=credentials))

    ch = connection.channel()
    routingkey = 'digikey_store_goods'
    url = 'http://www.digikey.cn/product-detail/zh/te-connectivity-measurement-specialties/02291335-000/356-1075-ND/735368'
    cat_id = 1
    goods_id = 1
    goods_sn = '1'
    is_first = False
    pdf_url = 'http://www.osram-os.com/Graphics/XPic2/00195908_0.pdf'
    lgs = LieGoodsSpider(cat_id, goods_id, goods_sn, url, pdf_url, ch, routingkey,
        is_first)
    html = lgs.goods()
    lgs.parse_goods(html)
