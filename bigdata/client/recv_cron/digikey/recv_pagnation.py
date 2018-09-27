# 每天跑一次获取每个分类的分页里的goods基本信息，不包括点进去到详情那里。
import pika
from threading import Thread, active_count
from client.settings import rabbitmq_server
from client.spider.digikey import lie_goods_pagination_spider
from requests.exceptions import (ConnectionError, ConnectTimeout, 
        ContentDecodingError)
from pika.exceptions import ChannelClosed
import logging
import time
import traceback

# 这个用于接收分页请求
DIGIKEY_PAGNATION = 'digikey_pagnation'
# 这用于通知大陆这边存储goods基础信息
DIGIKEY_STORE_PAGNATION = 'digikey_store_pagnation'
PROXY_IP = 'proxy_ip_digikey'


def get_rabbitmq_conn():
    user = rabbitmq_server['user']
    password = rabbitmq_server['password']
    host = rabbitmq_server['host']

    credentials = pika.PlainCredentials(user, password)
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host=host, credentials=credentials,
            socket_timeout=1000, channel_max=2, retry_delay=50))
    return connection

def serv_forever():
    global DIGIKEY_PAGNATION, DIGIKEY_STORE_PAGNATION
    connection = get_rabbitmq_conn()
    recv_channel = connection.channel()
    recv_channel.queue_declare(queue=DIGIKEY_PAGNATION)

    recv_channel.basic_qos(prefetch_count=20)
    recv_channel.basic_consume(callback,
                          queue=DIGIKEY_PAGNATION,
                          no_ack=False)

    print('waiting pagnation task')
    recv_channel.start_consuming()

def callback(ch, method, properties, body):
    global DIGIKEY_STORE_PAGNATION, send_channel
    while 1:
        if active_count() >= 15:
            print('线程池已满载')
            time.sleep(2)
        else:
            break
    print(" [x] Received %s %s" % (body, time.ctime()))

    cup = eval(body)
    cat_id = cup[0]
    url = cup[1]
    page = cup[2]
    try:
        ch.queue_declare(queue=DIGIKEY_STORE_PAGNATION)
        Thread(target=access_goods_list_by_page, args=(
            cat_id, url, page, ch, method, DIGIKEY_STORE_PAGNATION)).start()
        '''
        access_goods_list_by_page(cat_id, url, page, ch, method,
            DIGIKEY_STORE_PAGNATION)
        '''
    except Exception as e:
        print(e)

    print('pagnation complete')
    print('waiting pagnation task')
    
def access_goods_list_by_page(cat_id, url, page, send_channel, method,
        DIGIKEY_STORE_PAGNATION):
    try:
        global PROXY_IP
        lgps = lie_goods_pagination_spider.LieGoodsPaginationSpider(
                cat_id, url, send_channel, DIGIKEY_STORE_PAGNATION)
        html = lgps.next(page, PROXY_IP)
        lgps.parse_next(html)
    except ConnectionError as e:
        print(e)
        print('我拔网线了')
    except ConnectTimeout as e:
        print(e)
        print('我拔网线了')
        print('连接超时了')
    except Exception as e:
        print(e)
        print('我拔网线了')
        exstr = traceback.format_exc()
        print(exstr)
    send_channel.basic_ack(delivery_tag = method.delivery_tag)

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    serv_forever()
