# 更新新品
import pika
from threading import Thread, active_count
from client.settings import rabbitmq_server
from client.spider.digikey.new_goods import new_goods_spider
from requests.exceptions import (ConnectionError, ConnectTimeout, 
        ContentDecodingError)
from pika.exceptions import ChannelClosed
import logging
import time
import traceback

DIGIKEY_NEW_GOODS = 'digikey_new_goods'
DIGIKEY_STORE_NEW_GOODS = 'digikey_store_new_goods'
PROXY_IP = 'proxy_ip_digikey'

RBMQ = ''
CH = ''

def get_rabbitmq_conn():
    global RBMQ
    user = rabbitmq_server['user']
    password = rabbitmq_server['password']
    host = rabbitmq_server['host']

    credentials = pika.PlainCredentials(user, password)
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host=host, credentials=credentials,
            socket_timeout=500, channel_max=2, retry_delay=50))
    RBMQ = connection
    return connection

def serv_forever():
    global DIGIKEY_NEW_GOODS
    connection = get_rabbitmq_conn()
    recv_channel = connection.channel()
    recv_channel.queue_declare(queue=DIGIKEY_NEW_GOODS, durable=True)

    recv_channel.basic_qos(prefetch_count=15)
    recv_channel.basic_consume(callback,
                          queue=DIGIKEY_NEW_GOODS,
                          no_ack=False)

    print('waiting new goods task')
    recv_channel.start_consuming()

def callback(ch, method, properties, body):
    global DIGIKEY_STORE_NEW_GOODS
    print(" [x] Received %s %s" % (body, time.ctime()))

    cup = eval(body)
    cat_id = cup['cat_id']
    url = cup['url']
    try:
        ch.queue_declare(queue=DIGIKEY_STORE_NEW_GOODS, durable=True)
        Thread(target=access_all_new_goods_list, args=(
            cat_id, url, ch, method, DIGIKEY_STORE_NEW_GOODS)).start()
        '''
        access_all_new_goods_list(cat_id, url, ch, method,
            DIGIKEY_STORE_NEW_GOODS)
        '''
    except Exception as e:
        print(e)

    print('new goods complete')
    print('waiting new goods task')
    
def access_all_new_goods_list(cat_id, url, send_channel, method,
        DIGIKEY_STORE_NEW_GOODS):
    global PROXY_IP
    try:
        ngs = new_goods_spider.NewGoodsSpider(
                cat_id, url, send_channel, DIGIKEY_STORE_NEW_GOODS)
        html = ngs.get_total_page(PROXY_IP)
        ngs.parse_get_total_page(html,PROXY_IP)
    except ConnectionError as e:
        print(e)
        print('我拔网线了')
    except ConnectTimeout as e:
        print(e)
        print('连接超时了')
    except Exception as e:
        print(e)
        print('我拔网线了')
        exstr = traceback.format_exc()
        print(exstr)
    finally:
        send_channel.basic_ack(delivery_tag = method.delivery_tag)

if __name__ == '__main__':
    try:
        serv_forever()
    except Exception as e:
        print(e)
        CH.close()
        RBMQ.close()
