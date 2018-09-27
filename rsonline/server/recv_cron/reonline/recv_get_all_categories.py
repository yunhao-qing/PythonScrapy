# 接收所有分类数据并入库， 每天大概只跑一次
import pika
from server.settings import rabbitmq_server
from server.db.rsonline import mysql_client

rsonline_STORE_ALL_CATEGORIES = 'rsonline_store_all_categories'

def callback(ch, method, properties, body):
    categories = eval(body)
    print(categories)

    for cat in categories:
        cat_id = mysql_client.LieCategory.get_cat_id_by_cat_name(cat['cat_name'])
        if cat_id is None:
            lc_0 = mysql_client.LieCategory()
            for k, v in cat.items():
                if k == 'sub_categories':
                    continue
                lc_0[k] = v
            mysql_client.LieCategory.addLieCategory(lc_0)
            print(lc_0)
        else:
            #TODO
            pass

        for sub_cat in cat['sub_categories']:
            sub_cat_id = mysql_client.LieCategory.get_cat_id_by_cat_name(
                    sub_cat['cat_name'])
            if sub_cat_id is None:
                lc_1 = mysql_client.LieCategory()
                for k, v in sub_cat.items():
                    if k == 'sub_categories':
                        continue
                    lc_1[k] = v
                parent_id = mysql_client.LieCategory.get_cat_id_by_cat_name(
                        lc_1['parent_id'])
                lc_1['parent_id'] = parent_id
                mysql_client.LieCategory.addLieCategory(lc_1)
                print(lc_1)
            else:
                #TODO
                pass
            for sub_sub_cat in sub_cat['sub_categories']:
                sub_sub_cat_id = mysql_client.LieCategory.get_cat_id_by_cat_name(
                        sub_sub_cat['cat_name'])
                if sub_sub_cat_id is None:
                    lc_2 = mysql_client.LieCategory()
                    for k, v in sub_sub_cat.items():
                        if k == 'sub_categories':
                            continue
                        lc_2[k] = v
                    parent_id = mysql_client.LieCategory.get_cat_id_by_cat_name(
                            lc_2['parent_id'])
                    lc_2['parent_id'] = parent_id
                    mysql_client.LieCategory.addLieCategory(lc_2)
                    print(lc_2)
                else:
                    #TODO
                    pass

    ch.basic_ack(delivery_tag=method.delivery_tag)
    print('update categories complete')
    print('waiting store categories task')

def main():
    global rsonline_STORE_ALL_CATEGORIES
    host = rabbitmq_server['host']
    user = rabbitmq_server['user']
    password = rabbitmq_server['password']
    credentials = pika.PlainCredentials(user, password)
    connection = pika.BlockingConnection(pika.ConnectionParameters(
            host=host, credentials=credentials))
    channel = connection.channel()
    channel.basic_qos(prefetch_count=1)
    channel.queue_declare(queue=rsonline_STORE_ALL_CATEGORIES)
    channel.basic_consume(callback, queue=rsonline_STORE_ALL_CATEGORIES, 
            no_ack=False)
    print('waiting store categories task')
    channel.start_consuming()

if __name__ == '__main__':
    main()
