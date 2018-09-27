from server.db.alliedelec import mysql_client
from server.settings import rabbitmq_server
import pika

ALLIEDELEC_PAGNATION = 'alliedelec_pagnation'

def get_rb_conn():
    user = rabbitmq_server['user']
    password = rabbitmq_server['password']
    host = rabbitmq_server['host']
    credentials = pika.PlainCredentials(user, password)
    connection = pika.BlockingConnection(pika.ConnectionParameters(
            host=host, credentials=credentials))

    return connection

def main():
    global ALLIEDELEC_PAGNATION
    conn = get_rb_conn()
    ch = conn.channel()
    ch.queue_declare(queue=ALLIEDELEC_PAGNATION)

    cups = mysql_client.LieCategory.get_all_cat_id_url_page_count()

    for cup in cups:
        cat_id = cup['cat_id']
        url = cup['url']
        page_count = cup['page_count']
        msg = {'cat_id': cat_id, 'url': url}
        i = 1
        while i <= page_count:
            msg['page'] = i
            body = str(msg)
            ch.basic_publish(exchange='', routing_key=ALLIEDELEC_PAGNATION,
                    body=body)
            print('Sent [page=%d]' % i, body)
            i += 1

    mysql_client.ALLIEDELEC_CONN.close()

if __name__ == '__main__':
    main()
