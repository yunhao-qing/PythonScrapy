import pymongo

def get_mongo_con():
    connection = pymongo.MongoClient('192.168.1.88', 27017)
    db = connection.ichunt
    connection.close()
    return db


PROXY_IP_CONN = get_mongo_con()

class ProxyIP(dict):
    #proxie = "{'http': 'http://1.1.1.1:80'}"

    @classmethod
    def get_all_prxoyIPs(cls):
        '''
        method:
        parmas:
            a int 描述
        :return:
            str 描述 例: {asfsafa'afsd]
        '''
        global PROXY_IP_CONN
        ip_list=PROXY_IP_CONN.ips
        new_ips = []
        for item in ip_list.find():
            new_ips.append(item['ip'])
        return new_ips

    @classmethod
    def get_all_checkedIPs(cls):
        global PROXY_IP_CONN
        ip_checked_list = PROXY_IP_CONN.ips_checked
        new_ips = []
        for item in ip_checked_list.find():
            new_ips.append(item['ip'])
        return new_ips

if __name__ == "__main__":
    a=ProxyIP.get_all_prxoyIPs()
    print(type(a))
    print(len(a))


