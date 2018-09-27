import pika
from server.settings import rabbitmq_server
from server.db.digikey.mysql_client import LieGoods, DIGIKEY_CONN
import time
import sys

DIGIKEY_GOODS = 'digikey_goods'

def init():
    global DIGIKEY_GOODS
    user = rabbitmq_server['user']
    password = rabbitmq_server['password']
    host = rabbitmq_server['host']
    credentials = pika.PlainCredentials(user, password)
    connection = pika.BlockingConnection(pika.ConnectionParameters(
            host=host, credentials=credentials))
    channel = connection.channel()
    channel.queue_declare(queue=DIGIKEY_GOODS, durable=False)
    return channel

def send_task(channel, cat_id, goods_id, goods_sn, url, pdf_url):
    body = str([cat_id, goods_id, goods_sn, url, pdf_url])
    channel.basic_publish(exchange='',
                          routing_key=DIGIKEY_GOODS,
                          properties=pika.BasicProperties(
                              delivery_mode=2,  # make message persistent
                          ),
                          body=body)
    print(" [x] Sent %d %d %s %s %s\n" % (
        cat_id, goods_id, goods_sn, url, pdf_url))

def asc_send(channel, total_pages):
    first_goods_id = LieGoods.get_first_goods_id()
    i = 1
    while i <= total_pages:
        cgups = LieGoods.get_cat_id_goods_id_goods_sn_site_url_pdf_url_by_page(
                first_goods_id + (i-1) * 100)
        for cgup in cgups:
            cat_id = cgup['cat_id']
            goods_id = cgup['goods_id']
            goods_sn = cgup['goods_sn']
            url = cgup['site_url']
            pdf_url = cgup['pdf_url']

            print(" [x] Page %d" % i)
            send_task(channel, cat_id, goods_id, goods_sn, url, pdf_url)
        time.sleep(1)
        i += 1

def desc_send(channel, total_pages):
    last_goods_id = LieGoods.get_last_goods_id()
    i = 1
    while i <= total_pages:
        cgups = LieGoods.get_cat_id_goods_id_goods_sn_site_url_pdf_url_by_page_desc(
                last_goods_id - (i-1) * 100)
        for cgup in cgups:
            cat_id = cgup['cat_id']
            goods_id = cgup['goods_id']
            goods_sn = cgup['goods_sn']
            url = cgup['site_url']
            pdf_url = cgup['pdf_url']

            print(" [x] Page %d" % i)
            send_task(channel, cat_id, goods_id, goods_sn, url, pdf_url)
        time.sleep(1)
        i += 1

def main(asc_desc):
    channel = init()
    count = LieGoods.get_count()
    if not count:
        return
    total_pages = count // 100
    if total_pages % 100 != 0:
        total_pages += 1

    if asc_desc == 2:
        desc_send(channel, total_pages)
    elif asc_desc == 1:
        asc_send(channel, total_pages)
    
    DIGIKEY_CONN.close()

if __name__ == '__main__':
    now = time.time()
    if len(sys.argv) != 2:
        print('参数不正确，请使用排序方式, python3.6 send_goods.py asc/desc')
        sys.exit(-1)
    else:
        if sys.argv[1] == 'asc':
            main(1)
        elif sys.argv[1] == 'desc':
            main(2)
    print('共用时:', time.time() - now)
