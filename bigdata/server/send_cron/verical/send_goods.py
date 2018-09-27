from server.db.verical import mysql_client
import pika
from server.settings import rabbitmq_server
import time
import sys

VERICAL_GOODS = 'verical_goods'

def get_rb_conn():
    user = rabbitmq_server['user']
    password = rabbitmq_server['password']
    host = rabbitmq_server['host']
    credentials = pika.PlainCredentials(user, password)
    connection = pika.BlockingConnection(pika.ConnectionParameters(
            host=host, credentials=credentials))

    return connection

def main():
    global VERICAL_GOODS
    conn = get_rb_conn()
    ch = conn.channel()
    ch.queue_declare(queue=VERICAL_GOODS, durable=False)

    if sys.argv[1] == 'asc':
        asc(ch)
    if sys.argv[1] == 'desc':
        desc(ch)

def asc(ch):
    count = mysql_client.LieGoods.get_count()
    if not count:
        return
    total_pages = count // 100
    if total_pages % 100 != 0:
        total_pages += 1

    first_goods_id = mysql_client.LieGoods.get_first_goods_id()
    i = 1
    while i <= total_pages:
        cggups = mysql_client.LieGoods.\
                get_cat_id_goods_id_goods_name_goods_sn_site_url_pdf_url_by_page(
                first_goods_id + (i-1) * 100)
        for cggup in cggups:
            print(" [x] Page %d" % i, cggup)
            ch.basic_publish(exchange='', routing_key=VERICAL_GOODS,
                        properties=pika.BasicProperties(
                            delivery_mode=2,  # make message persistent
                        ),
                        body=str(cggup))
        time.sleep(1)
        i += 1


def desc(ch):
    count = mysql_client.LieGoods.get_count()
    if not count:
        return
    total_pages = count // 100
    if total_pages % 100 != 0:
        total_pages += 1

    first_goods_id = mysql_client.LieGoods.get_last_goods_id()
    i = 1
    while i <= total_pages:
        cggups = mysql_client.LieGoods.\
                get_cat_id_goods_id_goods_name_goods_sn_site_url_pdf_url_by_page(
                first_goods_id - (i-1) * 100)
        for cggup in cggups:
            print(" [x] Page %d" % i, cggup)
            ch.basic_publish(exchange='', routing_key=VERICAL_GOODS,
                        properties=pika.BasicProperties(
                            delivery_mode=2,  # make message persistent
                        ),
                        body=str(cggup))
        time.sleep(1)
        i += 1

if __name__ == '__main__':
    main()
    mysql_client.VERICAL_CONN.close()
