from server.db.verical import mysql_client
from server.settings import rabbitmq_server
import pika

VERICAL_PAGNATION = 'verical_pagnation'

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

    ckps = mysql_client.LieCategory.get_all_cat_id_keywords_page_count()

    for ckp in ckps:
        cat_id = ckp['cat_id']
        keywords = ckp['keywords']
        page_count = ckp['page_count']
        msg = {'cat_id': cat_id, 'keywords': keywords}
        i = 1
        while i <= page_count:
            msg['page'] = i
            body = str(msg)
            ch.basic_publish(exchange='', routing_key=VERICAL_PAGNATION,
                    body=body)
            print('Sent [page=%d]' % i, body)
            i += 1

    mysql_client.VERICAL_CONN.close()

if __name__ == '__main__':
    main()
