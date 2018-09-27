from server.db.avnet import mysql_client
from server.settings import rabbitmq_server
import pika

AVNET_GET_TOTAL_PAGES = 'avnet_get_total_pages'

def get_rb_conn():
    user = rabbitmq_server['user']
    password = rabbitmq_server['password']
    host = rabbitmq_server['host']
    credentials = pika.PlainCredentials(user, password)
    connection = pika.BlockingConnection(pika.ConnectionParameters(
            host=host, credentials=credentials))

    return connection

def main():
    global AVNET_GET_TOTAL_PAGES
    conn = get_rb_conn()
    ch = conn.channel()
    ch.queue_declare(queue=AVNET_GET_TOTAL_PAGES)

    cus = mysql_client.LieCategory.get_all_cat_id_url()
    for cu in cus:
        body = str(cu)
        ch.basic_publish(exchange='',
                routing_key=AVNET_GET_TOTAL_PAGES, body=body)
        print('Sent [cat_id=%d, url=%s]' % (cu['cat_id'], cu['url']))

    mysql_client.AVNET_CONN.close()

if __name__ == '__main__':
    main()
