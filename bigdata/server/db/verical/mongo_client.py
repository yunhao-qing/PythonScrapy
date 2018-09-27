from server.db import connection_pool

VERICAL_CONN = connection_pool.get_mongo_conn_no_auth('mongo_verical')

class Verical(dict):
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
    def addVerical(cls, verical):
        code = 'VERICAL_CONN.verical.insert_one(%s).inserted_id'
        code = code % str(verical)
        eval(code)

    @classmethod
    def replace_one_by_goods_id(cls, goods_id, verical):
        code = 'VERICAL_CONN.verical.replace_one({"goods_id": %d}, %s)'
        code = code % (goods_id, str(verical))
        eval(code)

    @classmethod
    def getVerical_by_goods_sn(cls, goods_sn):
        code = 'VERICAL_CONN.verical.find_one({"goods_sn":"%s"})'
        code = code % goods_sn
        return eval(code)

    @classmethod
    def getVerical_by_goods_id(cls, goods_id):
        code = 'VERICAL_CONN.verical.find_one({"goods_id":%d})'
        code = code % goods_id
        return eval(code)
