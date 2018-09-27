# 每天跑一次, 更新所有分类
import pika
from client.settings import rabbitmq_server
from client.spider.avnet import lie_category_spider
import time
import pprint
import base64

AVNET_STORE_ALL_CATEGORIES = 'avnet_store_all_categories'

def main():
    global AVNET_STORE_ALL_CATEGORIES
    host = rabbitmq_server['host']
    user = rabbitmq_server['user']
    password = rabbitmq_server['password']
    credentials = pika.PlainCredentials(user, password)
    connection = pika.BlockingConnection(pika.ConnectionParameters(
            host=host, credentials=credentials))
    channel = connection.channel()
    channel.queue_declare(queue=AVNET_STORE_ALL_CATEGORIES)

    lcs = lie_category_spider.LieCategorySpider()
    html = lcs.get_all_categories()
    categories = lcs.parse_get_all_categories(html)

    if categories is None:
        print('获取列表失败')
        connection.close()
        return
    body = str(categories)
    log_msg = {
        '时间': time.ctime(),
        '数据': categories
    }

    pprint.pprint(log_msg)
    channel.basic_publish(exchange='', routing_key=AVNET_STORE_ALL_CATEGORIES,
            body=body)

    connection.close()

if __name__ == '__main__':
    main()
