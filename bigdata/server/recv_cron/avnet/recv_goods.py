import pika
from server.settings import rabbitmq_server
from server.db.avnet import mysql_client, mongo_client
import time
import threading
import traceback

AVNET_STORE_GOODS = 'avnet_store_goods'

def callback(ch, method, properties, body):
    body = eval(body)
    print(body)
    try:
        for k, v in body.items():
            if k == '1':
                #TODO
                brand_id = mysql_client.LieBrand.get_brand_id_by_brand_name(v['provider_name'])
                if brand_id is None:
                    brand_id = 0
                v['brand_id'] = brand_id
                mysql_client.LieGoods.update_goods(v)
                break
            if k == '2':
                #TODO
                goods_id = mongo_client.Avnet.getAvnet_by_goods_id(v['goods_id'])
                if goods_id is None:
                    mongo_client.Avnet.addAvnet(v)
                else:
                    mongo_client.Avnet.replace_one_by_goods_id(v['goods_id'], v)
                break
            if k == "3":
                brand_id = mysql_client.LieBrand.get_brand_id_by_brand_name(v['brand_name'])
                if brand_id is None:
                    mysql_client.LieBrand.addLieBrand(v)
                break
            if k == '4':
                #TODO
                goods_id = mysql_client.LieGoodsPrice.exist(v['goods_id'])
                if goods_id is None:
                    mysql_client.LieGoodsPrice.addLieGoodsPrice(v)
                break
    except Exception as e:    
        exstr = traceback.format_exc()
        print(exstr)
        
    ch.basic_ack(delivery_tag = method.delivery_tag)

def edit_mongo(v):
    now = time.time()
    print('更新mongo')

    print('更新mongo用时', time.time() - now)

def main():
    global AVNET_STORE_GOODS
    host = rabbitmq_server['host']
    user = rabbitmq_server['user']
    password = rabbitmq_server['password']
    credentials = pika.PlainCredentials(user, password)
    connection = pika.BlockingConnection(pika.ConnectionParameters(
            host=host, credentials=credentials))
    channel = connection.channel()
    channel.queue_declare(queue=AVNET_STORE_GOODS, durable=True)
    channel.basic_qos(prefetch_count=200)
    channel.basic_consume(callback, queue=AVNET_STORE_GOODS, no_ack=False)
    print('waiting store goods task')
    channel.start_consuming()

if __name__ == '__main__':
    main()
