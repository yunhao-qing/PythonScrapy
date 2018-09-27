import pika
from client.settings import rabbitmq_server
from threading import active_count, Thread
import time
from client.spider.verical import lie_goods_pagnation_spider
from multiprocessing import Process

VERICAL_PAGNATION = 'verical_pagnation'
VERICAL_STORE_PAGNATION = 'verical_store_pagnation'
PROXY_IP = 'proxy_ip_verical'

def get_rb_conn():
    user = rabbitmq_server['user']
    password = rabbitmq_server['password']
    host = rabbitmq_server['host']
    credentials = pika.PlainCredentials(user, password)
    connection = pika.BlockingConnection(pika.ConnectionParameters(
            host=host, credentials=credentials))

    return connection

def main():
    global VERICAL_PAGNATION
    conn = get_rb_conn()
    ch = conn.channel()
    ch.queue_declare(queue=VERICAL_PAGNATION)

    ch.basic_qos(prefetch_count=20)
    ch.basic_consume(callback, queue=VERICAL_PAGNATION,
            no_ack=False)
    print('waiting pagnation task')
    ch.start_consuming()

def callback(ch, method, properties, body):
    print('Received ', body, time.ctime())

    body = eval(body)

    try:
        ch.queue_declare(queue=VERICAL_STORE_PAGNATION)
        cat_id = body['cat_id']
        keywords = body['keywords']
        page = body['page']
        Thread(target=call_spider, args=(cat_id, keywords, ch, method,
            page)).start()
    except Exception as e:
        print(e)


def call_spider(cat_id, keywords, ch, method, page):
    global VERICAL_STORE_PAGNATION, PROXY_IP
    try:
        lgps = lie_goods_pagnation_spider.LieGoodsPagnationSpider(cat_id, 
                keywords, ch, VERICAL_STORE_PAGNATION)
        html = lgps.pagnation(page)
        lgps.parse_pagnation(html)
    except BaseException as e:
        print(e)
    ch.basic_ack(delivery_tag = method.delivery_tag)

if __name__ == '__main__':
    main()
