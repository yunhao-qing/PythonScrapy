from server.db import connection_pool

AVNET_CONN = connection_pool.get_mongo_conn_no_auth('mongo_avnet')

class Avnet(dict):
    goods_id = ''
    goods_sn = ''
    goods_name = ''
    brand_name = ''
    goods_price = ''
    dt = ''
    desc = ''
    docurl = ''
    pn = ''
    stock = ''
    tiered = ''
    increment = ''
    time = ''
    url = ''

    @classmethod
    def addAvnet(cls, avnet):
        code = 'AVNET_CONN.avnet.insert_one(%s).inserted_id'
        code = code % str(avnet)
        eval(code)

    @classmethod
    def replace_one_by_goods_id(cls, goods_id, avnet):
        code = 'AVNET_CONN.avnet.replace_one({"goods_id": %d}, %s)'
        code = code % (goods_id, str(avnet))
        eval(code)

    @classmethod
    def getAvnet_by_goods_sn(cls, goods_sn):
        code = 'AVNET_CONN.avnet.find_one({"goods_sn":"%s"})'
        code = code % goods_sn
        return eval(code)

    @classmethod
    def getAvnet_by_goods_id(cls, goods_id):
        code = 'AVNET_CONN.avnet.find_one({"goods_id":%d})'
        code = code % goods_id
        return eval(code)
