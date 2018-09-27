import pika
from server.settings import rabbitmq_server
from server.db.verical import mysql_client, mongo_client
import time
import threading
import traceback

VERICAL_STORE_GOODS = 'verical_store_goods'

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

                goods_id = v['goods_id']
                if goods_id == -1:
                    print('一个产品对应多个商家')
                    tmp = mysql_client.LieGoods.get_goods_id_by_goods_sn(
                            v['goods_sn'])
                    
                    if tmp is None:
                        del v['goods_id']
                        g = mysql_client.LieGoods.\
                                get_goods_by_goods_sn(
                                        v['goods_sn'].split('_')[0])
                        del g['goods_id']
                        g['goods_sn'] = v['goods_sn']
                        
                        mysql_client.LieGoods.addLieGoods(g)
                    else:
                        v['goods_id'] = tmp
                        mysql_client.LieGoods.update_goods(v)
                else:
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
                    if v['goods_id'] == -1:
                        tmp = mysql_client.LieGoods.get_goods_id_by_goods_sn(
                                v['goods_sn'])
                        if tmp is not None:
                            if mysql_client.LieGoodsPrice.exist(tmp) is None:
                                v['goods_id'] = tmp
                                mysql_client.LieGoodsPrice.addLieGoodsPrice(v)
                    else:
                        mysql_client.LieGoodsPrice.addLieGoodsPrice(v)

    except Exception as e:    
        exstr = traceback.format_exc()
        print(exstr)
        
    ch.basic_ack(delivery_tag = method.delivery_tag)

def edit_mongo(v):
    now = time.time()
    print('更新mongo')
    verical = v
    if verical['goods_id'] != -1:
        exist_verical = mongo_client.Verical.getVerical_by_goods_id(
                v['goods_id'])
        print('正在更新mongo')
        if not exist_verical:
            print('这个数据在mongo里不存在, 增加mongo')
            mongo_client.Verical.addVerical(verical)
        else:
            print('这个数据在mongo里存在，替换mongo')
            goods_id = verical['goods_id']
            mongo_client.Verical.replace_one_by_goods_id(goods_id, verical)
    else:
        m_goods_id = mysql_client.LieGoods.get_goods_id_by_goods_sn(v['goods_sn'])
        if m_goods_id is not None:
            v_goods_id = mongo_client.Verical.getVerical_by_goods_id(m_goods_id)
            if v_goods_id is not None:
                verical['goods_id'] = m_goods_id
                mongo_client.Verical.replace_one_by_goods_id(m_goods_id, verical)
            else:
                verical['goods_id'] = m_goods_id
                mongo_client.Verical.addVerical(verical)

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
    channel.queue_declare(queue=VERICAL_STORE_GOODS, durable=True)
    channel.basic_qos(prefetch_count=200)
    channel.basic_consume(callback, queue=VERICAL_STORE_GOODS, no_ack=False)
    print('waiting store goods task')
    channel.start_consuming()

if __name__ == '__main__':
    main()
