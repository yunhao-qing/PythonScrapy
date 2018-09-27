# 每天跑一次，获取所有分类的总页数
import pika
from threading import Thread, active_count
from client.settings import rabbitmq_server
from client.spider.digikey import lie_goods_pagination_spider
from requests.exceptions import (ConnectionError, ConnectTimeout, 
        ContentDecodingError)
from pika.exceptions import ChannelClosed
import logging
import time

DIGIKEY_GET_TOTAL_PAGE = 'digikey_get_total_page'
DIGIKEY_STORE_TOTAL_PAGE = 'digikey_store_total_page'
PROXY_IP = 'proxy_queue_digikey'

def get_rabbitmq_conn():
    user = rabbitmq_server['user']
    password = rabbitmq_server['password']
    host = rabbitmq_server['host']

    credentials = pika.PlainCredentials(user, password)
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host=host, credentials=credentials,socket_timeout=30))
    return connection

def serv_forever():
    global DIGIKEY_GET_TOTAL_PAGE
    connection = get_rabbitmq_conn()
    recv_channel = connection.channel()

    recv_channel.queue_declare(queue=DIGIKEY_GET_TOTAL_PAGE)

    recv_channel.basic_qos(prefetch_count=10)
    recv_channel.basic_consume(callback,
                          queue=DIGIKEY_GET_TOTAL_PAGE,
                          no_ack=False)

    print('waiting get total_page task')
    recv_channel.start_consuming()

def callback(ch, method, properties, body):
    global DIGIKEY_STORE_TOTAL_PAGE
    print(" [x] Received %s %s" % (body, time.ctime()))

    cup = eval(body)
    cat_id = cup[0]
    url = cup[1]

    ch.queue_declare(queue=DIGIKEY_STORE_TOTAL_PAGE)
    Thread(target=access_goods_list_by_page, args=(
        cat_id, url, ch, method,DIGIKEY_STORE_TOTAL_PAGE)).start()

    print('get total_page complete')
    print('waiting get total_page task')
    
def access_goods_list_by_page(cat_id, url, send_channel,method,
        DIGIKEY_STORE_TOTAL_PAGE):
    try:
        global PROXY_IP
        lgps = lie_goods_pagination_spider.LieGoodsPaginationSpider(
            cat_id=cat_id, url=url, channel=send_channel, 
            routingkey=DIGIKEY_STORE_TOTAL_PAGE)
        html = lgps.get_total_page(PROXY_IP)
        lgps.parse_get_total_page(html)
    except ConnectionError as e:
        print('我拔网线了')

    except ConnectTimeout as e:
        print('连接超时了')
    send_channel.basic_ack(delivery_tag = method.delivery_tag)

if __name__ == '__main__':
    serv_forever()
