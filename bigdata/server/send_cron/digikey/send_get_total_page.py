import pika
from server.db.digikey import mysql_client
from server.settings import rabbitmq_server

DIGIKEY_GET_TOTAL_PAGE = 'digikey_get_total_page'

def main():
    global DIGIKEY_PAGNATION
    user = rabbitmq_server['user']
    password = rabbitmq_server['password']
    host = rabbitmq_server['host']
    credentials = pika.PlainCredentials(user, password)
    connection = pika.BlockingConnection(pika.ConnectionParameters(
            host=host, credentials=credentials))
    channel = connection.channel()
    channel.queue_declare(queue=DIGIKEY_GET_TOTAL_PAGE)

    count = mysql_client.LieCategory.get_count()
    if not count:
        print('居然没有东西')
        return

    total_pages = count // 100
    if total_pages % 100 != 0:
        total_pages += 1

    i = 1
    while i <= total_pages:
        cups = mysql_client.LieCategory.get_all_cat_id_url_page_count_by_page(i)
        for cup in cups:
            cat_id = cup['cat_id']
            url = cup['url']
            page_count = cup['page_count']
            body = str([cat_id, url])
            channel.basic_publish(exchange='', 
                    routing_key=DIGIKEY_GET_TOTAL_PAGE,
                    body=body)
            print(" [x] Sent %d %s\n" % (cat_id, url))
        i += 1

    mysql_client.DIGIKEY_CONN.close()

if __name__ == '__main__':
    main()
