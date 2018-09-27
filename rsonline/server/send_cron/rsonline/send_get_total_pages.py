from server.db.rsonline import mysql_client
from server.settings import rabbitmq_server
import pika

rsonline_GET_TOTAL_PAGES = 'rsonline_get_total_pages'

def get_rb_conn():
    user = rabbitmq_server['user']
    password = rabbitmq_server['password']
    host = rabbitmq_server['host']
    credentials = pika.PlainCredentials(user, password)
    connection = pika.BlockingConnection(pika.ConnectionParameters(
            host=host, credentials=credentials))

    return connection

def main():
    global rsonline_GET_TOTAL_PAGES
    conn = get_rb_conn()
    ch = conn.channel()
    ch.queue_declare(queue=rsonline_GET_TOTAL_PAGES)

    ckus = mysql_client.LieCategory.get_all_cat_id_keywords_url()
    for cku in ckus:
        body = str(cku)
        cat_id = cku['cat_id']
        keywords = cku['keywords']
        url = cku['url']
        ch.basic_publish(exchange='',
                routing_key=rsonline_GET_TOTAL_PAGES, body=body)
        print('Sent [cat_id=%d, keywords=%s,url=%s]' % (cat_id, keywords,url))

    mysql_client.rsonline_CONN.close()

if __name__ == '__main__':
    main()
