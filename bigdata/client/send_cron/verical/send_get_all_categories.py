# 每天跑一次, 更新所有分类
import pika
from client.settings import rabbitmq_server
from client.spider.verical import lie_category_spider
import time
import pprint

VERICAL_STORE_ALL_CATEGORIES = 'verical_store_all_categories'

def main():
    global VERICAL_STORE_ALL_CATEGORIES
    host = rabbitmq_server['host']
    user = rabbitmq_server['user']
    password = rabbitmq_server['password']
    credentials = pika.PlainCredentials(user, password)
    connection = pika.BlockingConnection(pika.ConnectionParameters(
            host=host, credentials=credentials))
    channel = connection.channel()
    channel.queue_declare(queue=VERICAL_STORE_ALL_CATEGORIES)

    lcs = lie_category_spider.LieCategorySpider()
    html = lcs.get_all_categories()
    categories = lcs.parse_get_all_categories(html)

    body = str(categories)
    log_msg = {
        '时间': time.ctime(),
        '数据': categories
    }

    pprint.pprint(log_msg)
    channel.basic_publish(exchange='', routing_key=VERICAL_STORE_ALL_CATEGORIES,
            body=body)

if __name__ == '__main__':
    main()
