# 接收goods基础信息数据并入库
import pika
from server.settings import rabbitmq_server
from server.db.avnet import mysql_client

AVNET_STORE_PAGNATION = 'avnet_store_pagnation'

def callback(ch, method, properties, body):
    body = eval(body)
    for k, v in body.items():
        if k == '1':
            goods_id = mysql_client.LieGoods.get_goods_id_by_goods_sn(v['goods_sn'])
            if goods_id is None:
                mysql_client.LieGoods.addLieGoods(v)

    ch.basic_ack(delivery_tag = method.delivery_tag)
    print('store pagnation complete')
    print('waiting store pagnation task')

def main():
    global AVNET_STORE_PAGNATION
    host = rabbitmq_server['host']
    user = rabbitmq_server['user']
    password = rabbitmq_server['password']
    credentials = pika.PlainCredentials(user, password)
    connection = pika.BlockingConnection(pika.ConnectionParameters(
            host=host, credentials=credentials))
    channel = connection.channel()
    channel.queue_declare(queue=AVNET_STORE_PAGNATION)
    channel.basic_qos(prefetch_count=200)
    channel.basic_consume(callback, queue=AVNET_STORE_PAGNATION, no_ack=False)
    print('waiting store pagnation task')
    channel.start_consuming()

if __name__ == '__main__':
    main()
