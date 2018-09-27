from client.spider.avnet import lie_goods_pagnation_spider
import pika
from client.settings import rabbitmq_server
from threading import Thread, active_count
import time
import traceback

AVNET_GET_TOTAL_PAGES = 'avnet_get_total_pages'
AVNET_STORE_GET_TOTAL_PAGES = 'avnet_store_get_total_pages'
PROXY_IP = 'proxy_ip_avnet'

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
        '''
        call_spider(ch, cat_id, url, method)
        '''
    except Exception as e:
        print(e)

    print('get total_page complete')
    print('waiting get total_page task')

def call_spider(ch, cat_id, url, method):
    global AVNET_STORE_GET_TOTAL_PAGES, PROXY_IP
    try:
        ch.queue_declare(queue=AVNET_STORE_GET_TOTAL_PAGES)
        lgps = lie_goods_pagnation_spider.LieGoodsPagnationSpider(cat_id, url,
                ch, AVNET_STORE_GET_TOTAL_PAGES)
        html = lgps.get_total_pages(PROXY_IP)
        if html is None:
            print('访问异常，重新推入队列')
            body = str({'cat_id': cat_id, 'url': url})
            ch.basic_publish(exchange='',
                    routing_key=AVNET_GET_TOTAL_PAGES, body=body)
            print('Sent', body)
        else:
            lgps.parse_get_total_pages(html)
    except Exception as e:
        print('解析异常，重新推入队列')
        body = str({'cat_id': cat_id, 'url': url})
        ch.basic_publish(exchange='',
                routing_key=AVNET_GET_TOTAL_PAGES, body=body)
        print('Sent', body)
        ex = traceback.format_exc()
        print(ex)
    finally:
        ch.basic_ack(delivery_tag = method.delivery_tag)
        print('线程任务已确认')

def main():
    global AVNET_GET_TOTAL_PAGES

    conn = get_rb_conn()
    ch = conn.channel()
    ch.basic_qos(prefetch_count=10)
    ch.queue_declare(queue=AVNET_GET_TOTAL_PAGES)

    ch.basic_consume(callback, queue=AVNET_GET_TOTAL_PAGES, no_ack=False)
    print('waiting get total page task')
    ch.start_consuming()

if __name__ == '__main__':
    main()
