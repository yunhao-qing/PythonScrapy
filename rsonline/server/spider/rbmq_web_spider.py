import requests
from server.settings import auth, web_url

class RBMQWebSpider:
    def get_data(self):
        url = web_url
        self.session = requests.session()
        self.session.auth = auth
        r = self.session.get(url)
        self.session.close()
        return r.text

    def parse_get_data(self, html):
        if not html:
            return
        html = html.replace('null', "''")
        html = html.replace('false', "False")
        html = html.replace('true', "True")
        return eval(html)
        
    def get_proxy_ip_data(self, proxy_queue, data):
        proxy_ip_data = {}
        for d in data:
            if proxy_queue in d.values():
                proxy_ip_data = d
        return proxy_ip_data

if __name__ == '__main__':
    import pprint
    rs = RBMQWebSpider()
    d = rs.get_data()
    print('proxy_ip' in d)
    d = rs.parse_get_data(d)
    #pprint.pprint(d)
    print(rs.get_proxy_ip_data(d))
