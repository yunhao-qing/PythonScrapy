import pika
from server.settings import rabbitmq_server
from server.db.digikey.mysql_client import LieGoods, DIGIKEY_CONN
import time

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
    channel.queue_declare(queue=DIGIKEY_GOODS, durable=True)
    return channel

def send_task(channel, cat_id, goods_id, goods_sn, url, pdf_url):
    body = str([cat_id, goods_id, goods_sn, url, pdf_url])
    channel.basic_publish(exchange='',
                          routing_key=DIGIKEY_GOODS,
                          body=body)
    print(" [x] Sent %d %d %s %s %s\n" % (
        cat_id, goods_id, goods_sn, url, pdf_url))

def main():
    channel = init()
    count = LieGoods.get_count_no_goods_name()
    if not count:
        return
    total_pages = count // 100
    if total_pages % 100 != 0:
        total_pages += 1

    first_goods_id = LieGoods.get_first_goods_id()
    i = 1
    while i <= total_pages:
        cgups = LieGoods.get_cat_id_goods_id_goods_sn_site_url_pdf_url_by_page_no_goods_name(
                first_goods_id + (i-1) * 100)
        for cgup in cgups:
            cat_id = cgup['cat_id']
            goods_id = cgup['goods_id']
            goods_sn = cgup['goods_sn']
            url = cgup['site_url']
            pdf_url = cgup['pdf_url']

            print(" [x] Page %d" % i)
            send_task(channel, cat_id, goods_id, goods_sn, url, pdf_url)
        i += 1

    DIGIKEY_CONN.close()

if __name__ == '__main__':
    main()
