import pika
from server.db.digikey import mysql_client, mongo_client
from server.settings import rabbitmq_server
import time
import logging
import traceback

DIGIKEY_STORE_NEW_GOODS = 'digikey_store_new_goods'

def callback(ch, method, properties, body): 
    body = eval(body)
    try:
        deal_data(body)
    except Exception as e:
        print(e)
        exstr = traceback.format_exc()
        print(exstr)

    ch.basic_ack(delivery_tag = method.delivery_tag)
    print('store goods task complete')
    print('waiting store goods task')

def deal_data(body):
    for k, v in body.items():
        goods_id = mysql_client.LieGoods.get_goods_id_by_goods_sn(v['goods_sn'])
        v['goods_id'] = goods_id

        if k == "1":
            brand_id = mysql_client.LieBrand.get_brand_id_by_brand_name(
                    v['provider_name'])
            v['brand_id'] = brand_id if brand_id else 0
            if v['goods_id'] is None:
                mysql_client.LieGoods.addLieGoods(v)

        elif k == "2":
            #增加 brand
            lieBrand = v['lieBrand']
            cat_id = v['cat_id']
            goods_id = v['goods_id']
            attrs = v['attrs']

            brand_id = mysql_client.LieBrand.get_brand_id_by_brand_name(
                    lieBrand['brand_name'])
            if not brand_id:
                print('增加band')
                mysql_client.LieBrand.addLieBrand(lieBrand)

            # 增加 attr
            for k, v in attrs.items():
                lca = mysql_client.LieCategoryAttr()
                lca['attr_name'] = k.encode().decode()
                lca['cat_id'] = cat_id
                attr_id = mysql_client.LieCategoryAttr.\
                        get_attr_id_by_attr_name(lca['attr_name'])
                if not attr_id:
                    print('增加category attr [*] %s' % lca['attr_name'])
                    mysql_client.LieCategoryAttr.addLieCategoryAttr(lca)
                    attr_id = mysql_client.LieCategoryAttr.\
                            get_attr_id_by_attr_name(lca['attr_name'])
                ext_id = mysql_client.LieGoodsAttr.\
                        get_ext_id_by_goods_id_attr_name(
                                    goods_id, lca['attr_name'])
                if not ext_id:
                    lga = mysql_client.LieGoodsAttr()
                    lga['goods_id'] = goods_id
                    lga['cat_id'] = cat_id
                    lga['attr_id'] = attr_id
                    lga['attr_name'] = lca['attr_name']
                    lga['attr_value'] = v.encode().decode()
                    print('增加goods attr')
                    mysql_client.LieGoodsAttr.addLieGoodsAttr(lga)
        elif k == "3":
            edit_mongo(v)
        elif k == "4":
            goods_price = str(v['goods_price'])
            goods_id = v['goods_id']
            lgs = mysql_client.LieGoodsPrice()
            lgs['goods_id'] = goods_id
            lgs['price'] = goods_price

            if mysql_client.LieGoodsPrice.exist(goods_id) is None:
                mysql_client.LieGoodsPrice.addLieGoodsPrice(lgs)

def edit_mongo(v):
    dgk = v['dgk']
    goods_id = v['goods_id']
    if goods_id is None:
        return
    dgk['goods_id'] = goods_id
    print('封装后的mongo数据')
    print(dgk)
    exist_dgk = mongo_client.Digikey.getDigikey_by_goods_id(goods_id)
    print('正在更新mongo')
    if not exist_dgk:
        print('这个数据在mongo里不存在, 增加mongo')
        mongo_client.Digikey.addDigikey(dgk)
    else:
        print('这个数据在mongo里存在，替换mongo')
        mongo_client.Digikey.replace_one_by_goods_id(goods_id, dgk)

def main():
    global DIGIKEY_STORE_NEW_GOODS
    host = rabbitmq_server['host']
    user = rabbitmq_server['user']
    password = rabbitmq_server['password']
    credentials = pika.PlainCredentials(user, password)
    connection = pika.BlockingConnection(pika.ConnectionParameters(
            host=host, credentials=credentials))
    channel = connection.channel()
    channel.basic_qos(prefetch_count=200)
    channel.queue_declare(queue=DIGIKEY_STORE_NEW_GOODS, durable=True)
    channel.basic_consume(callback, queue=DIGIKEY_STORE_NEW_GOODS, no_ack=False)
    print('waiting store new goods task')
    channel.start_consuming()

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    main()
