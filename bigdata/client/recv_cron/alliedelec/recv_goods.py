import pika
from client.settings import rabbitmq_server
from threading import active_count, Thread
import time
from client.spider.alliedelec import lie_goods_spider
import sys
import traceback
from multiprocessing import Process

ALLIEDELEC_GOODS = 'alliedelec_goods'
ALLIEDELEC_STORE_GOODS = 'alliedelec_store_goods'
PROXY_IP = 'proxy_ip_alliedelec'

def get_rb_conn():
    user = rabbitmq_server['user']
    password = rabbitmq_server['password']
    host = rabbitmq_server['host']
    credentials = pika.PlainCredentials(user, password)
    connection = pika.BlockingConnection(pika.ConnectionParameters(
            host=host, credentials=credentials))

    return connection

IS_FIRST = False

def main(is_first):
    global ALLIEDELEC_GOODS, IS_FIRST
    IS_FIRST = is_first
    print(IS_FIRST)
    conn = get_rb_conn()
    ch = conn.channel()
    ch.queue_declare(queue=ALLIEDELEC_GOODS, durable=True)
    ch.basic_qos(prefetch_count=15)
    ch.basic_consume(callback, queue=ALLIEDELEC_GOODS,
            no_ack=False)
    print('waiting goods task')
    ch.start_consuming()

def callback(ch, method, properties, body):
    global ALLIEDELEC_STORE_GOODS

    print('Received', body, time.ctime())
    body = eval(body)
    try:
        cat_id = body['cat_id']
        goods_id = body['goods_id']
        goods_name = body['goods_name']
        goods_sn = body['goods_sn']
        site_url = body['site_url']
        pdf_url = body['pdf_url']
        goods_thumb = body['goods_thumb']
        goods_desc = body['goods_desc']
        provider_name = body['provider_name']
        ch.queue_declare(queue=ALLIEDELEC_STORE_GOODS, durable=True)
        Thread(target=call_spider, args=(cat_id, goods_id, goods_name, goods_sn, 
            site_url, pdf_url, goods_thumb, goods_desc, provider_name, ch, 
            method)).start()
    except Exception as e:
        print(e)
        extstr = traceback.format_exc()
        '''
        with open('/data/log/bigdata/ALLIEDELEC/ALLIEDELEC_线程异常', 'a') as f:
            f.write(time.ctime() + '\n')
            f.write(str(body) +'\n')
            f.write(extstr + '\n')
        '''
        print(extstr)

    print('goods task complete')
    print('waiting goods task')

def call_spider(cat_id, goods_id, goods_name, goods_sn,site_url, pdf_url, 
        goods_thumb, goods_desc, provider_name, ch, method):
    global ALLIEDELEC_STORE_GOODS, IS_FIRST, PROXY_IP, ALLIEDELEC_GOODS
    try:
        lgs = lie_goods_spider.LieGoodsSpider(cat_id,goods_id,goods_name, 
            goods_sn,site_url,goods_thumb, goods_desc, provider_name, ch, 
            ALLIEDELEC_STORE_GOODS, IS_FIRST)
        html = lgs.goods(PROXY_IP)
        if html is None:
            body = dict()
            body['cat_id'] = cat_id
            body['goods_id'] = goods_id
            body['goods_name'] = goods_name
            body['goods_sn'] = goods_sn
            body['site_url'] = site_url
            body['pdf_url'] = pdf_url
            body['goods_thumb'] = goods_thumb
            body['goods_desc'] = goods_desc
            body['provider_name'] = provider_name
            ch.basic_publish(exchange='', routing_key=ALLIEDELEC_GOODS,
                properties=pika.BasicProperties(
                    delivery_mode=2,  # make message persistent
                ),
                body=str(body))
            print('需要重新推入队列')
        else:
            lgs.parse_goods(html)
    except Exception as e:
        extstr = traceback.format_exc()
        print(extstr)
        '''
        with open('/data/log/bigdata/ALLIEDELEC/ALLIEDELEC_调用爬虫异常.txt', 'a') as f:
            f.write(time.ctime() + '\n')
            f.write(str([cat_id, goods_id, goods_name, goods_sn]) + '\n')
            f.write(extstr + '\n')
        '''

    ch.basic_ack(delivery_tag = method.delivery_tag)

if __name__ == '__main__':
    print(sys.argv)
    if len(sys.argv) == 1:
        IS_FIRST = True
    else:
        IS_FIRST = False
    print('开关起作用了', IS_FIRST)
    main(IS_FIRST)
