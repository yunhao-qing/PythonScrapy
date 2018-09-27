from client.spider.alliedelec import lie_goods_pagnation_spider 
import pika
from client.settings import rabbitmq_server
from threading import Thread, active_count
import time

ALLIEDELEC_GET_TOTAL_PAGES = 'alliedelec_get_total_pages'
ALLIEDELEC_STORE_GET_TOTAL_PAGES = 'alliedelec_store_get_total_pages'
PROXY_IP = 'proxy_ip_alliedelec'

def get_rb_conn():
    user = rabbitmq_server['user']
    password = rabbitmq_server['password']
    host = rabbitmq_server['host']
    credentials = pika.PlainCredentials(user, password)
    connection = pika.BlockingConnection(pika.ConnectionParameters(
            host=host, credentials=credentials))

    return connection

def callback(ch, method, properties, body):
    body = eval(body)

    print('Receive', body)

    cat_id = body['cat_id']
    url = body['url']
    try:
        Thread(target=call_spider, args=(ch, cat_id, url, method)).start()
    except Exception as e:
        print(e)

    print('get total_page complete')
    print('waiting get total_page task')

def call_spider(ch, cat_id, url, method):
    global ALLIEDELEC_STORE_GET_TOTAL_PAGES, PROXY_IP
    try:
        ch.queue_declare(queue=ALLIEDELEC_STORE_GET_TOTAL_PAGES)
        lgps = lie_goods_pagnation_spider.LieGoodsPagnationSpider(
                cat_id, url, ch, ALLIEDELEC_STORE_GET_TOTAL_PAGES)
        html = lgps.get_total_pages(PROXY_IP)
        lgps.parse_get_total_pages(html)
    except Exception as e:
        print(e)
    ch.basic_ack(delivery_tag = method.delivery_tag)

def main():
    global ALLIEDELEC_GET_TOTAL_PAGES

    conn = get_rb_conn()
    ch = conn.channel()
    ch.basic_qos(prefetch_count=10)
    ch.queue_declare(queue=ALLIEDELEC_GET_TOTAL_PAGES)

    ch.basic_consume(callback, queue=ALLIEDELEC_GET_TOTAL_PAGES, no_ack=False)
    print('waiting get total page task')
    ch.start_consuming()

if __name__ == '__main__':
    main()
