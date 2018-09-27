import pika

PROXY_IP = 'proxy_ip'

rabbitmq_server = {
    'host':  '192.168.1.88',
    'user':  'admin',
    'password': '123456'
}

def ch_init():
    host = rabbitmq_server['host']
    user = rabbitmq_server['user']
    password = rabbitmq_server['password']
    credentials = pika.PlainCredentials(user, password)
    connection = pika.BlockingConnection(pika.ConnectionParameters(
            host=host, credentials=credentials))
    channel = connection.channel()
    return channel

CH = ch_init()

class Spider:
    def __init__(self):
        pass

    def proxies(self):
        global PROXY_IP, CH
        proxies = {}

        try:
            method_frame, header_frame, body = CH.basic_get(queue=PROXY_IP,
                    no_ack=True)
            if method_frame:
                print(method_frame, header_frame, body)
                body = eval(body)
                protocol = body['protocol']
                ip = body['ip']
                port = body['port']
                proxies[protocol] = protocol+'://'+ip+':'+port
                print(proxies)
            else:
                print('No message returned')
        except Exception as e:
            print(e)
        return proxies

if __name__ == '__main__':
    Spider()
