# 接收总页数，并入库 
import pika
from server.settings import rabbitmq_server
from server.db.digikey import mysql_client

DIGIKEY_STORE_TOTAL_PAGE = 'digikey_store_total_page'

def callback(ch, method, properties, body):
    body = eval(body)
    for k, v in body.items():
        if k == '1':
            mysql_client.LieCategory.update_lie_category_page_count_by_cat_id(
                    v[0], v[1])
        if k == '2':
            goods_id = mysql_client.LieGoods.get_goods_id_by_goods_sn(
                    v['goods_sn'])
            if goods_id is not None:
               mysql_client.LieGoods.update_goods(v)

    ch.basic_ack(delivery_tag=method.delivery_tag)
    print('store total page complete')
    print('waiting store total page task')

def main():
    global DIGIKEY_STORE_TOTAL_PAGE
    host = rabbitmq_server['host']
    user = rabbitmq_server['user']
    password = rabbitmq_server['password']
    credentials = pika.PlainCredentials(user, password)
    connection = pika.BlockingConnection(pika.ConnectionParameters(
            host=host, credentials=credentials))
    channel = connection.channel()
    channel.basic_qos(prefetch_count=200)
    channel.queue_declare(queue=DIGIKEY_STORE_TOTAL_PAGE)
    channel.basic_consume(callback, queue=DIGIKEY_STORE_TOTAL_PAGE, no_ack=False)
    print('waiting store total page task')
    
    channel.start_consuming()

if __name__ == '__main__':
    main()
