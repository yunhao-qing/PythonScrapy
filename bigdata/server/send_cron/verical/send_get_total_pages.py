from server.db.verical import mysql_client
from server.settings import rabbitmq_server
import pika

VERICAL_GET_TOTAL_PAGES = 'verical_get_total_pages'

def get_rb_conn():
    user = rabbitmq_server['user']
    password = rabbitmq_server['password']
    host = rabbitmq_server['host']
    credentials = pika.PlainCredentials(user, password)
    connection = pika.BlockingConnection(pika.ConnectionParameters(
            host=host, credentials=credentials))

    return connection

def main():
    global VERICAL_GET_TOTAL_PAGES
    conn = get_rb_conn()
    ch = conn.channel()
    ch.queue_declare(queue=VERICAL_GET_TOTAL_PAGES)

    cks = mysql_client.LieCategory.get_all_cat_id_keywords()
    for ck in cks:
        body = str(ck)
        ch.basic_publish(exchange='',
                routing_key=VERICAL_GET_TOTAL_PAGES, body=body)
        print('Sent [cat_id=%d, keywords=%s]' % (ck['cat_id'], ck['keywords']))

    mysql_client.VERICAL_CONN.close()

if __name__ == '__main__':
    main()
