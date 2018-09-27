import yaml, os, os.path, pymongo
import mysql.connector
from urllib.parse import quote_plus
import logging

def get_dbcfg():
    dbcfgpath = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),'db.yaml')
    stream = open(dbcfgpath, 'r')
    dbcfg = yaml.load(stream)
    stream.close()
    return dbcfg

DBCFG = get_dbcfg()

def get_mysql_conn(db_key_name):
    config = DBCFG[db_key_name]
    conn = mysql.connector.connect(**config)
    return conn

def get_mongo_conn_need_auth(db_key_name):
    mongo_cfg = DBCFG[db_key_name]
    username = mongo_cfg['username']
    password = mongo_cfg['password']
    host = mongo_cfg['host']
    database = mongo_cfg['database']
    uri = "mongodb://%s:%s@%s" % (
            quote_plus(username), quote_plus(password), host)
    mongo_conn = pymongo.MongoClient(uri)
    mongo_conn = eval('mongo_conn.%s' % database)
    return mongo_conn

def get_mongo_conn_no_auth(db_key_name):
    mongo_cfg = DBCFG[db_key_name]
    mongo_conn = pymongo.MongoClient(mongo_cfg['host'])
    mongo_conn = eval('mongo_conn.%s' % mongo_cfg['database'])
    return mongo_conn
