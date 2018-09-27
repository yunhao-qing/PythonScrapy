from server.db import connection_pool

ALLIEDELEC_CONN = connection_pool.get_mongo_conn_no_auth('mongo_alliedelec')

class Alliedelec(dict):
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
    def addAlliedelec(cls, alliedelec):
        code = 'ALLIEDELEC_CONN.alliedelec.insert_one(%s).inserted_id'
        code = code % str(alliedelec)
        eval(code)

    @classmethod
    def replace_one_by_goods_id(cls, goods_id, alliedelec):
        code = 'ALLIEDELEC_CONN.alliedelec.replace_one({"goods_id": %d}, %s)'
        code = code % (goods_id, str(alliedelec))
        eval(code)

    @classmethod
    def getAlliedelec_by_goods_sn(cls, goods_sn):
        code = 'ALLIEDELEC_CONN.alliedelec.find_one({"goods_sn":"%s"})'
        code = code % goods_sn
        return eval(code)

    @classmethod
    def getAlliedelec_by_goods_id(cls, goods_id):
        code = 'ALLIEDELEC_CONN.alliedelec.find_one({"goods_id":%d})'
        code = code % goods_id
        return eval(code)
