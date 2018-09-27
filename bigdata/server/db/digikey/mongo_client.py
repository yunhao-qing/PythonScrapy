from server.db import connection_pool
from datetime import datetime
import time

DIGIKEY_CONN = connection_pool.get_mongo_conn_no_auth('mongo_digikey')

class Digikey(dict):
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
    def addDigikey(cls, digikey):
        code = 'DIGIKEY_CONN.digikey.insert(%s)'
        code = code % str(digikey)
        eval(code)

    @classmethod
    def replace_one_by_goods_id(cls, goods_id, digikey):
        code = 'DIGIKEY_CONN.digikey.replace_one({"goods_id": %d}, %s)'
        code = code % (goods_id, str(digikey))
        eval(code)

    @classmethod
    def getDigikey_by_goods_sn(cls, goods_sn):
        code = 'DIGIKEY_CONN.digikey.find_one({"goods_sn":"%s"})'
        code = code % goods_sn
        return eval(code)

    @classmethod
    def getDigikey_by_goods_id(cls, goods_id):
        code = 'DIGIKEY_CONN.digikey.find_one({"goods_id":%d})'
        code = code % goods_id
        return eval(code)

    @classmethod
    def getDigikey_not_update(cls):
        now = datetime.today()
        now = str(now.replace(hour=0,minute=0,second=0, microsecond=0))
        now = time.mktime(time.strptime(now,'%Y-%m-%d %H:%M:%S'))
        code = 'DIGIKEY_CONN.digikey.find({"time": {"$lt": %d}})' % now
        return eval(code)

    @classmethod
    def getDigikey_not_update_count(cls):
        now = datetime.today()
        now = str(now.replace(hour=0,minute=0,second=0, microsecond=0))
        now = time.mktime(time.strptime(now,'%Y-%m-%d %H:%M:%S'))
        code = 'DIGIKEY_CONN.digikey.find({"time": {"$lt": %d}}).count()' % now
        return eval(code)
