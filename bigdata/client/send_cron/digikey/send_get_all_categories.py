# 每天跑一次, 更新所有分类
import pika
from client.settings import rabbitmq_server
from client.spider.digikey import lie_category_spider
import time
import pprint

DIGIKEY_STORE_ALL_CATEGORIES = 'digikey_store_all_categories'

def main():
    global DIGIKEY_STORE_ALL_CATEGORIES
    host = rabbitmq_server['host']
    user = rabbitmq_server['user']
    password = rabbitmq_server['password']
    credentials = pika.PlainCredentials(user, password)
    connection = pika.BlockingConnection(pika.ConnectionParameters(
            host=host, credentials=credentials))
    channel = connection.channel()
    channel.queue_declare(queue=DIGIKEY_STORE_ALL_CATEGORIES)

    lcs = lie_category_spider.LieCategorySpider()
    html = lcs.products()
    categories = lcs.parse_products(html)

    body = str(categories)
    log_msg = {
        '时间': time.ctime(),
        '数据': categories
    }

    pprint.pprint(log_msg)
    channel.basic_publish(exchange='', routing_key=DIGIKEY_STORE_ALL_CATEGORIES,
            body=body)

if __name__ == '__main__':
    main()
