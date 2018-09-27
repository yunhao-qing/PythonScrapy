from server.db.avnet import mysql_client
from server.settings import rabbitmq_server
import pika

AVNET_PAGNATION = 'avnet_pagnation'

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

    ckps = mysql_client.LieCategory.get_all_cat_id_url_page_count_ext_fields()

    for ckp in ckps:
        print(ckp)
        cat_id = ckp['cat_id']
        url = ckp['url']
        page_count = ckp['page_count']
        pageid = ckp['ext_fields']
        msg = {'cat_id': cat_id, 'url': url, 'pageid': pageid}
        i = 1
        while i <= page_count:
            msg['page'] = i
            body = str(msg)
            ch.basic_publish(exchange='', routing_key=AVNET_PAGNATION,
                    body=body)
            print('Sent [page=%d]' % i, body)
            i += 1

    mysql_client.AVNET_CONN.close()

if __name__ == '__main__':
    main()
