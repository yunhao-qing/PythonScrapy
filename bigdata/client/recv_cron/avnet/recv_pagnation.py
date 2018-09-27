import pika
from client.settings import rabbitmq_server
from threading import active_count, Thread
import time
from client.spider.avnet import lie_goods_pagnation_spider
import traceback

AVNET_PAGNATION = 'avnet_pagnation'
AVNET_STORE_PAGNATION = 'avnet_store_pagnation'
PROXY_IP = 'proxy_ip_avnet'

def get_rb_conn():
    user = rabbitmq_server['user']
    password = rabbitmq_server['password']
    host = rabbitmq_server['host']
    credentials = pika.PlainCredentials(user, password)
    connection = pika.BlockingConnection(pika.ConnectionParameters(
            host=host, credentials=credentials))

    return connection

def main():
    global AVNET_PAGNATION
    conn = get_rb_conn()
    ch = conn.channel()
    ch.queue_declare(queue=AVNET_PAGNATION)

    ch.basic_qos(prefetch_count=5)
    ch.basic_consume(callback, queue=AVNET_PAGNATION,
            no_ack=False)
    print('waiting pagnation task')
    ch.start_consuming()

def callback(ch, method, properties, body):
    print('Received ', body, time.ctime())

    body = eval(body)

    try:
        ch.queue_declare(queue=AVNET_STORE_PAGNATION)
        cat_id = body['cat_id']
        url = body['url']
        page = body['page']
        pageid = body['pageid']
        Thread(target=call_spider, args=(cat_id, url, pageid, ch, method,
            page)).start()
        #call_spider(cat_id, url, pageid, ch, method, page)
    except Exception as e:
        print(e)

def call_spider(cat_id, url, pageid, ch, method, page):
    global AVNET_STORE_PAGNATION, PROXY_IP
    try:
        lgps = lie_goods_pagnation_spider.LieGoodsPagnationSpider(cat_id, 
                url, ch, AVNET_STORE_PAGNATION)
        html = lgps.pagnation(pageid, page, PROXY_IP)
        if html is None:
            print('访问异常，重新推入队列')
            body = str({'cat_id': cat_id, 'ur':url, 'page':page})
            ch.basic_publish(exchange='', routing_key=AVNET_PAGNATION,
                    body=body)
        else:
            lgps.parse_pagnation(html)
    except Exception as e:
        print(e)
        ex = traceback.format_exc()
        print(ex)
        print('解析异常，重新推入队列')
        body = str({'cat_id': cat_id, 'ur':url, 'page':page})
        ch.basic_publish(exchange='', routing_key=AVNET_PAGNATION,
                body=body)
    finally:
        ch.basic_ack(delivery_tag = method.delivery_tag)
        print('线程任务已确认')

if __name__ == '__main__':
    main()
