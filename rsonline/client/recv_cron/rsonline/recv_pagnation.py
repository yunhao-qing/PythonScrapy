import pika
from client.settings import rabbitmq_server
from threading import Thread
import time
from client.spider.rsonline import lie_goods_pagnation_spider

rsonline_PAGNATION = 'rsonline_pagnation'
rsonline_STORE_PAGNATION = 'rsonline_store_pagnation'
PROXY_IP = 'proxy_ip_rsonline'

def get_rb_conn():
    user = rabbitmq_server['user']
    password = rabbitmq_server['password']
    host = rabbitmq_server['host']
    credentials = pika.PlainCredentials(user, password)
    connection = pika.BlockingConnection(pika.ConnectionParameters(
            host=host, credentials=credentials))
    return connection

def main():
    global rsonline_PAGNATION
    conn = get_rb_conn()
    ch = conn.channel()
    ch.queue_declare(queue=rsonline_PAGNATION)

    ch.basic_qos(prefetch_count=1)
    ch.basic_consume(callback, queue=rsonline_PAGNATION,
            no_ack=False)
    print('waiting pagnation task')
    ch.start_consuming()

def callback(ch, method, properties, body):
    print('Received ', body, time.ctime())

    body = eval(body)

    try:
        ch.queue_declare(queue=rsonline_STORE_PAGNATION)
        cat_id = body['cat_id']
        url = body['url']
        page = body['page']
        Thread(target=call_spider, args=(cat_id, url, ch, method,
            page)).start()
    except Exception as e:
        print(e)


def call_spider(cat_id, url, ch, method, page):
    global rsonline_STORE_PAGNATION, PROXY_IP
    try:
        lgps = lie_goods_pagnation_spider.LieGoodsPagnationSpider(cat_id, 
                url, ch, rsonline_STORE_PAGNATION)
        html = lgps.pagnation(page)
        lgps.parse_pagnation(html)
    except BaseException as e:
        print(e)
    ch.basic_ack(delivery_tag = method.delivery_tag)
    print('线程任务已确认')

if __name__ == '__main__':
    main()
