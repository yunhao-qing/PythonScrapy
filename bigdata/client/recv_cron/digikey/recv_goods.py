from threading import Thread
import pika
import time
from client.settings import rabbitmq_server
from client.spider.digikey.lie_goods_spider import LieGoodsSpider
from requests.exceptions import (ConnectionError, ConnectTimeout, 
        ContentDecodingError)
from pika.exceptions import ChannelClosed, ConnectionClosed
import logging
import traceback
import sys

DIGIKEY_GOODS = 'digikey_goods'
DIGIKEY_STORE_GOODS = 'digikey_store_goods'
PROXY_IP = 'proxy_ip_digikey'
IS_FIRST = True

RBMQ = ''
CH = ''

def serv_forever(is_first):
    global DIGIKEY_GOODS, IS_FIRST, RBMQ, CH
    IS_FIRST = is_first
    print(IS_FIRST)
    user = rabbitmq_server['user']
    password = rabbitmq_server['password']
    host = rabbitmq_server['host']
    credentials = pika.PlainCredentials(user, password)
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host=host, credentials=credentials,
            socket_timeout=500, channel_max=2, retry_delay=50))
    RBMQ = connection
    channel = connection.channel()
    CH = channel

    channel.queue_declare(queue=DIGIKEY_GOODS ,durable=False)

    channel.basic_qos(prefetch_count=20)
    channel.basic_consume(callback,
                          queue=DIGIKEY_GOODS,
                          no_ack=False)

    print('waiting goods task')
    channel.start_consuming()

def callback(ch, method, properties, body):
    print(" [x] Received %s %s" % (body, time.ctime()))

    global DIGIKEY_STORE_GOODS
    cgup = eval(body)
    cat_id = int(cgup[0])
    goods_id = cgup[1]
    goods_sn = cgup[2]
    url = cgup[3]
    pdf_url = cgup[4]

    try:
        ch.queue_declare(queue=DIGIKEY_STORE_GOODS, durable=True)

        Thread(target=update_digikey, args=(
            cat_id, goods_id, goods_sn, url, pdf_url, ch, method,
            DIGIKEY_STORE_GOODS)).start()
        '''
        update_digikey( cat_id, goods_id, goods_sn, url, pdf_url, ch, method,
            DIGIKEY_STORE_GOODS)
        '''
    except Exception as e:
        print(e)
        exstr = traceback.format_exc()
        print(exstr)
        '''
        with open('/data/log/bigdata/digikey/digikey_goods_thread_exception.txt',
                'a') as f:
            f.write(time.ctime() + '->' + url + '\n' + str(exstr) + '\n')
        sys.exit(-1)
        '''

    print('goods task complete')
    print('waiting goods task')

def update_digikey(cat_id, goods_id, goods_sn, url, pdf_url, ch, method,
        DIGIKEY_STORE_GOODS):
    global IS_FIRST, PROXY_IP, DIGIKEY_GOODS
    lgsp = LieGoodsSpider(cat_id, goods_id, goods_sn, url, pdf_url, ch,
            DIGIKEY_STORE_GOODS, IS_FIRST)
    try:
        html = lgsp.goods(PROXY_IP)
        if html is None:
            print('url 重新推入队列' , url)
            body = str([cat_id, goods_id, goods_sn, url, pdf_url])
            ch.basic_publish(exchange='',
                                  routing_key=DIGIKEY_GOODS,
                                  properties=pika.BasicProperties(
                                      delivery_mode=2,  # make message persistent
                                  ),
                                  body=body)
            print(" [x] Sent %d %d %s %s %s\n" % (
                cat_id, goods_id, goods_sn, url, pdf_url))
        else:
            lgsp.parse_goods(html)
    except ConnectionClosed as e:
        exstr = traceback.format_exc()
        '''
        with open('/data/log/bigdata/digikey/digikey_goods_pika_connection_closed_exception.txt',
                'a') as f:
            f.write(time.ctime() + '->' + url + '\n' + str(exstr) + '\n')
        print('connection关闭',url, time.ctime())
        '''
        sys.exit(-1)

    except ChannelClosed as e:
        exstr = traceback.format_exc()
        '''
        with open('/data/log/bigdata/digikey/digikey_goods_pika_channel_closed_exception.txt',
                'a') as f:
            f.write(time.ctime() + '->' + url + '\n' + str(exstr) + '\n')
        print('channel关闭',url, time.ctime())
        '''
        sys.exit(-1)
    except AttributeError as be:
        print(be)
        exstr = traceback.format_exc()
        '''
        with open('/data/log/bigdata/digikey/digikey_goods_attribute_error.txt', 
                'a') as f:
            f.write(time.ctime() + '->' + url + '\n' + str(exstr) + '\n')

        print('错误',url, time.ctime())
        '''

    try:
        ch.basic_ack(delivery_tag = method.delivery_tag)
        print('线程任务已经确认')
    except Exception as e:
        print(e)
        exstr = traceback.format_exc()
        '''
        with open('/data/log/bigdata/digikey/digikey_goods_ack_error.txt', 
                'a') as f:
            f.write(time.ctime() + '->' + url + '\n' + str(exstr) + '\n')

        print('错误',url, time.ctime())
        sys.exit(-1)
        '''
        print(exstr)

if __name__ == '__main__':
    #logging.basicConfig(level=logging.DEBUG)
    if len(sys.argv) == 2:
        qo = sys.argv[1]
        if qo == 'True':
            IS_FIRST = True
        else:
            IS_FIRST = False
    if IS_FIRST == False:
        print('更新mongo')
    else:
        print('更新mysql')
    try:
        serv_forever(IS_FIRST)
    except Exception as e:
        print(e)
