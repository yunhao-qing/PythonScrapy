from server.db.avnet import mysql_client
from server.settings import rabbitmq_server
import pika

AVNET_STORE_GET_TOTAL_PAGES = 'avnet_store_get_total_pages'

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
    for k, v in body.items():
        if k == "1":
            mysql_client.LieCategory.\
                    update_lie_category_page_count_ext_fields_by_cat_id(
                    v['cat_id'], v['page_count'], v['pageid'])

            print('Stored [cat_id=%d, page_count=%d, pageid=%s' % (v['cat_id'], 
                v['page_count'], v['pageid']))
    ch.basic_ack(delivery_tag = method.delivery_tag)

def main():
    global AVNET_STORE_GET_TOTAL_PAGES
    conn = get_rb_conn()
    ch = conn.channel()
    ch.basic_qos(prefetch_count=5)   
    ch.queue_declare(queue=AVNET_STORE_GET_TOTAL_PAGES)

    ch.basic_consume(callback, queue=AVNET_STORE_GET_TOTAL_PAGES, no_ack=False)
    print('waiting store total page task')
    ch.start_consuming()

if __name__ == '__main__':
    main()
