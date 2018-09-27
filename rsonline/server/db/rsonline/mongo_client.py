from server.db import connection_pool

rs_CONN = connection_pool.get_mongo_conn_no_auth('mongo_rsonline')

class rsonline(dict):
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
    def addrsonline(cls, rsonline):
        code = 'rs_CONN.rsonline.insert_one(%s).inserted_id'
        code = code % str(rsonline)
        eval(code)

    @classmethod
    def replace_one_by_goods_id(cls, goods_id, rsonline):
        code = 'rs_CONN.rsonline.replace_one({"goods_id": %d}, %s)'
        code = code % (goods_id, str(rsonline))
        eval(code)

    @classmethod
    def getrsonline_by_goods_sn(cls, goods_sn):
        code = 'rs_CONN.rsonline.find_one({"goods_sn":"%s"})'
        code = code % goods_sn
        return eval(code)

    @classmethod
    def getrsonline_by_goods_id(cls, goods_id):
        code = 'rs_CONN.rsonline.find_one({"goods_id":%d})'
        code = code % goods_id
        return eval(code)
