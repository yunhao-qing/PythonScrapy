import pika
from server.settings import rabbitmq_server
from server.db.digikey import mysql_client
import time

DIGIKEY_NEW_GOODS = 'digikey_new_goods'

def rbmq_conn_init():
    global DIGIKEY_NEW_GOODS
    user = rabbitmq_server['user']
    password = rabbitmq_server['password']
    host = rabbitmq_server['host']

    credentials = pika.PlainCredentials(user, password)
    connection = pika.BlockingConnection(pika.ConnectionParameters(
        host=host, credentials=credentials))

    channel = connection.channel()
    channel.queue_declare(queue=DIGIKEY_NEW_GOODS, durable=True)
    return channel

def main():
    global DIGIKEY_NEW_GOODS
    ch = rbmq_conn_init()
    
    count = mysql_client.LieCategory.get_count()
    
    total_page = count / 100
    if total_page % 100 != 0:
        total_page += 1

    i = 1
    while i <= total_page:
        cups = mysql_client.LieCategory.get_all_cat_id_url_page_count_by_page(i)
        for cup in cups:
            cat_id = cup['cat_id']
            url = cup['url'] + '?newproducts=1'
            body = str({'cat_id': cat_id, 'url': url})
            print(body)
            ch.basic_publish(exchange='', routing_key=DIGIKEY_NEW_GOODS,
                    properties=pika.BasicProperties(
                      delivery_mode=2,  # make message persistent
                    ),
                    body=body)
        time.sleep(1)
        i += 1

    mysql_client.DIGIKEY_CONN.close()

if __name__ == '__main__':
    main()
