import pika

def init():
    credentials = pika.PlainCredentials(USER, PASSWORD)
    connection = pika.BlockingConnection(pika.ConnectionParameters(
            host=HOST, credentials=credentials))
    channel = connection.channel()
    channel.queue_declare(queue=PROXY_IPS)
    return channel

def send_task(channel,ip):
    channel.basic_publish(ip=ip)

def main():
    channel = init()
    for i in range(len(ips)):
        send_task(channel,ip[i])

if __name__ == '__main__':
    main()
