from server.db import connection_pool
import hashlib
import logging
import time

COMPANY_CONN = connection_pool.get_mongo_conn_no_auth('mongo_company')

class Company(dict):
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
    increment = ''  # default 1
    time = '' 
    url = ''

    @classmethod
    def addCompany(cls, company):
        code = 'COMPANY_CONN.company.insert_one(%s).inserted_id'
        code = code % str(company)
        eval(code)

    @classmethod
    def replace_one_by_goods_id(cls, goods_id, company):
        code = 'COMPANY_CONN.company.replace_one({"goods_id":%d}, %s)'
        code = code % (goods_id, str(company))
        eval(code)

    @classmethod
    def getCompany_by_goods_sn(cls, goods_sn_md5):
        code = 'COMPANY_CONN.company.find_one({"goods_sn": "%s"})' 
        code = code % (goods_sn_md5)
        return eval(code)
