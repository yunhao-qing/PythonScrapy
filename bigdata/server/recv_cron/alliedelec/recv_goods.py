import pika
from server.settings import rabbitmq_server
from server.db.alliedelec import mysql_client, mongo_client
import time
import threading
import traceback

ALLIEDELEC_STORE_GOODS = 'alliedelec_store_goods'

def callback(ch, method, properties, body):
    body = eval(body)
    print(body)
    try:
        for k, v in body.items():
            if k == '1':
                print('更新mysql')
                brand_id = mysql_client.LieBrand.get_brand_id_by_brand_name(
                        v['provider_name'])
                v['brand_id'] = brand_id if brand_id else 0
                mysql_client.LieGoods.update_goods(v)
                break
            if k == '2':
                edit_mongo(v)
                break
            if k == "3":
                brand_id = mysql_client.LieBrand.get_brand_id_by_brand_name(
                        v['brand_name'])
                if brand_id is None:
                    mysql_client.LieBrand.addLieBrand(v)
                break
            if k == '4':
                if mysql_client.LieGoodsPrice.exist(v['goods_id']) is None:
                    mysql_client.LieGoodsPrice.addLieGoodsPrice(v)
    except Exception as e:    
        exstr = traceback.format_exc()
        print(exstr)
        
    ch.basic_ack(delivery_tag = method.delivery_tag)

def edit_mongo(v):
    now = time.time()
    print('更新mongo')
    alliedelec = v
    exist_alliedelec = mongo_client.Alliedelec.getAlliedelec_by_goods_id(
            v['goods_id'])
    print('正在更新mongo')
    if not exist_alliedelec:
        print('这个数据在mongo里不存在, 增加mongo')
        mongo_client.Alliedelec.addAlliedelec(alliedelec)
    else:
        print('这个数据在mongo里存在，替换mongo')
        goods_id = alliedelec['goods_id']
        mongo_client.Verical.replace_one_by_goods_id(goods_id, alliedelec)

    print('更新mongo用时', time.time() - now)

def main():
    global VERICAL_STORE_GOODS
    host = rabbitmq_server['host']
    user = rabbitmq_server['user']
    password = rabbitmq_server['password']
    credentials = pika.PlainCredentials(user, password)
    connection = pika.BlockingConnection(pika.ConnectionParameters(
            host=host, credentials=credentials))
    channel = connection.channel()
    channel.queue_declare(queue=ALLIEDELEC_STORE_GOODS, durable=True)
    channel.basic_qos(prefetch_count=200)
    channel.basic_consume(callback, queue=ALLIEDELEC_STORE_GOODS, no_ack=False)
    print('waiting store goods task')
    channel.start_consuming()

if __name__ == '__main__':
    main()
