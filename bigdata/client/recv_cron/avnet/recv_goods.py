import pika
from client.settings import rabbitmq_server
from threading import active_count, Thread
import time
from client.spider.avnet import lie_goods_spider
import sys
import traceback
from multiprocessing import Process

AVNET_GOODS = 'avnet_goods'
AVNET_STORE_GOODS = 'avnet_store_goods'
PROXY_IP = 'proxy_ip_avnet'

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
    global AVNET_GOODS, IS_FIRST
    IS_FIRST = is_first
    print(IS_FIRST)
    conn = get_rb_conn()
    ch = conn.channel()
    ch.queue_declare(queue=AVNET_GOODS, durable=True)
    ch.basic_qos(prefetch_count=5)
    ch.basic_consume(callback, queue=AVNET_GOODS,
            no_ack=False)
    print('waiting goods task')
    ch.start_consuming()

def callback(ch, method, properties, body):
    global AVNET_STORE_GOODS

    print('Received', body, time.ctime())
    body = eval(body)
    try:
        cat_id = body['cat_id']
        goods_id = body['goods_id']
        goods_name = body['goods_name']
        goods_sn = body['goods_sn']
        goods_desc = body['goods_desc']
        goods_thumb = body['goods_thumb']
        site_url = body['site_url']
        ch.queue_declare(queue=AVNET_STORE_GOODS, durable=True)
        Thread(target=call_spider, args=(cat_id, goods_id, goods_name, goods_sn, 
            goods_desc, goods_thumb, site_url, ch, method)).start()
        '''
        call_spider(cat_id, goods_id, goods_name, goods_sn,goods_desc, goods_thumb, site_url, ch, method)
        '''
    except Exception as e:
        extstr = traceback.format_exc()
        print(extstr)

        print('线程异常，重新推入对列')
        body = dict()
        body['cat_id'] = cat_id
        body['goods_id'] = goods_id
        body['goods_name'] = goods_name
        body['goods_sn'] = goods_sn
        body['goods_desc'] = goods_desc
        body['goods_thumb'] = goods_thumb
        body['site_url'] = site_url
        ch.basic_publish(exchange='', routing_key=AVNET_GOODS,
            properties=pika.BasicProperties(
                delivery_mode=2,  # make message persistent
            ),
            body=str(body))

        '''
        with open('/data/log/bigdata/avnet/avnet_线程异常', 'a') as f:
            f.write(time.ctime() + '\n')
            f.write(str(body) +'\n')
            f.write(extstr + '\n')
        '''

    print('goods task complete')
    print('waiting goods task')

def call_spider(cat_id, goods_id, goods_name, goods_sn,goods_desc, goods_thumb, site_url, ch,
        method):
    global AVNET_STORE_GOODS, IS_FIRST, PROXY_IP, AVNET_GOODS
    html = ''
    try:
        lgs = lie_goods_spider.LieGoodsSpider(cat_id, goods_id, goods_name,
                goods_sn, goods_desc, goods_thumb, site_url, ch, AVNET_STORE_GOODS, IS_FIRST)
        html = lgs.goods(PROXY_IP)
        if html is None:
            print('访问异常，重新推入队列')
            body = dict()
            body['cat_id'] = cat_id
            body['goods_id'] = goods_id
            body['goods_name'] = goods_name
            body['goods_sn'] = goods_sn
            body['goods_desc'] = goods_desc
            body['goods_thumb'] = goods_thumb
            body['site_url'] = site_url
            ch.basic_publish(exchange='', routing_key=AVNET_GOODS,
                properties=pika.BasicProperties(
                    delivery_mode=2,  # make message persistent
                ),
                body=str(body))
        else:
            lgs.parse_goods(html)
    except Exception as e:
        extstr = traceback.format_exc()
        print(extstr)
        print('解析异常，重新推入对列', site_url)
        body = dict()
        body['cat_id'] = cat_id
        body['goods_id'] = goods_id
        body['goods_name'] = goods_name
        body['goods_sn'] = goods_sn
        body['goods_desc'] = goods_desc
        body['goods_thumb'] = goods_thumb
        body['site_url'] = site_url
        ch.basic_publish(exchange='', routing_key=AVNET_GOODS,
            properties=pika.BasicProperties(
                delivery_mode=2,  # make message persistent
            ),
            body=str(body))

        '''
        with open('/data/log/bigdata/AVNET/AVNET_调用爬虫异常.txt', 'a') as f:
            f.write(time.ctime() + '\n')
            f.write(str([cat_id, goods_id, goods_name, goods_sn]) + '\n')
            f.write(extstr + '\n')
        '''
    finally:
        ch.basic_ack(delivery_tag = method.delivery_tag)
        print('线程任务已确定')

if __name__ == '__main__':
    print(sys.argv)
    if len(sys.argv) == 1:
        IS_FIRST = True
    else:
        IS_FIRST = False
    print('开关起作用了', IS_FIRST)
    main(IS_FIRST)
