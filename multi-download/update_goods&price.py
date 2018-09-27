#-*- coding: UTF-8 -*-
import time
import mysql.connector
import datetime
from io import open
import logging
import multi_download
from itertools import islice

start_time = datetime.datetime.now()

multi_download.sftp_multi_download(hostname = '192.168.1.88',
                                   username = 'xiongbin',
                                   password = '123456',
                                   port = 22,
                                   local_dir = 'E:\\trial\\',
                                   remote_dir = '/home/xiongbin/store_feed/')

filename = "E:/trial/texas_instruments_inventory_feed.txt"

cnx = mysql.connector.connect(user = 'ichunt', password = 'ichunt',
                              host = '192.168.1.88',
                              database = 'excel')

cursor = cnx.cursor()

get_id = ("SELECT goods_id FROM lie_goods "
         "WHERE goods_name = %(goods_name)s"
         "  AND company_name = %(company_name)s AND moq = %(moq)s")


add_goods = ("INSERT INTO lie_goods (company_name,goods_name, "
             "goods_number,create_time,update_time,goods_desc,moq) "
            "VALUES (%(company_name)s,%(goods_name)s,%(goods_number)s,"
             "%(create_time)s,%(update_time)s, %(goods_desc)s,%(moq)s ) ")

add_price = ("INSERT INTO lie_goods_ladder_price "
             "(goods_num,rmb_price,dollor_price,goods_id) "
             "VALUES (%(gdno)s,%(rmbp)s, %(dolp)s, %(gdid)s)")

update_goods = ("UPDATE lie_goods SET goods_number = %(goods_number)s ,"
                "update_time = %(update_time)s "
                "WHERE goods_name = %(goods_name)s")


def convert_to_rmb(price):
    if price == "":
        return "0"
    else:
        b=float(price)*6.9
        return b


def break_line(a_line):
    a = a_line.split(",")
    a[22] = str(a_line)[-2]
    return a


def new_insert_goods(a):
    data_goods = {
        'company_name': a[0],
        'goods_name': a[1],
        'goods_number': a[3],
        'create_time': time.time(),
        'update_time': time.time(),
        'goods_desc': a[20],
        'moq': a[22]
    }
    cursor.execute(add_goods, data_goods)
    cnx.commit()


def new_insert_price(a):

    data = {
        'goods_name': a[1],
        'company_name': a[0],
        'moq': a[22]
    }
    cursor.execute(get_id, data)
    gdidd = cursor.fetchall()
    gdiddd = int(gdidd[0][0])

    if a[4] != "":
        data_price = {'gdno': a[4], 'rmbp': convert_to_rmb(a[5]), 'dolp': a[5], 'gdid': gdiddd, }
        cursor.execute(add_price, data_price)
        cnx.commit()
        if a[6] != "":
            data_price = {'gdno': a[6], 'rmbp': convert_to_rmb(a[7]), 'dolp': a[7], 'gdid': gdiddd, }
            cursor.execute(add_price, data_price)
            cnx.commit()
            if a[8] != "":
                data_price = {'gdno': a[8], 'rmbp': convert_to_rmb(a[9]), 'dolp': a[9], 'gdid': gdiddd, }
                cursor.execute(add_price, data_price)
                cnx.commit()
                if a[10] != "":
                    data_price = {'gdno': a[10], 'rmbp': convert_to_rmb(a[11]), 'dolp': a[11], 'gdid': gdiddd, }
                    cursor.execute(add_price, data_price)
                    cnx.commit()
                    if a[12] != "":
                        data_price = {'gdno': a[12], 'rmbp': convert_to_rmb(a[13]), 'dolp': a[13], 'gdid': gdiddd, }
                        cursor.execute(add_price, data_price)
                        cnx.commit()
                        if a[14] != "":
                            data_price = {'gdno': a[14], 'rmbp': convert_to_rmb(a[15]), 'dolp': a[15], 'gdid': gdiddd, }
                            cursor.execute(add_price, data_price)
                            cnx.commit()
                            if a[16] != "":
                                data_price = {'gdno': a[16], 'rmbp': convert_to_rmb(a[17]), 'dolp': a[17],
                                              'gdid': gdiddd, }
                                cursor.execute(add_price, data_price)
                                cnx.commit()
                                if a[18] != "":
                                    data_price = {'gdno': a[18], 'rmbp': convert_to_rmb(a[19]), 'dolp': a[19],
                                                  'gdid': gdiddd, }
                                    cursor.execute(add_price, data_price)
                                    cnx.commit()


def update_good(a):
    new_time=time.time()
    cursor.execute(update_goods,{'goods_number': a[3],
                                 'update_time': new_time,
                                 'goods_name': a[1]})
    cnx.commit()


def test_whether_exist(a):
    sql = ("SELECT goods_id FROM lie_goods "
           "WHERE goods_name = %(goods_name)s "
           "AND company_name = %(company_name)s "
           "AND  moq = %(moq)s"
           )
    args = {'goods_name': a[1],
            'company_name': a[0],
            'moq': a[22]
            }
    cursor.execute(sql, args)
    gdidd = cursor.fetchall()
    if gdidd:
        return 1
    else:
        return 0


def delete_old_price(a):
    data = {'goods_name': a[1],
            'company_name':a[0],
            'moq':a[22]}
    cursor.execute(get_id, data)
    gdidd = cursor.fetchall()
    gdiddd = int(gdidd[0][0])
    cursor.execute("DELETE FROM lie_goods_ladder_price "
                   "WHERE goods_id = %(goods_id)s",
                   {'goods_id': gdiddd}
                   )
    cnx.commit()


f= open(filename, 'rb')
lines = f.readlines()
update_amount = 0
insert_amount = 0


for l in islice(lines, 1, None):
    a = break_line(l)
    if test_whether_exist(a) == 1:
        update_good(a)
        delete_old_price(a)
        new_insert_price(a)
        update_amount = update_amount+1
    else:
        new_insert_goods(a)
        new_insert_price(a)
        insert_amount = insert_amount+1

cursor.close()
cnx.close()

end_time = datetime.datetime.now()
used_time = (end_time - start_time)

logger = logging.getLogger('logger')
logger.setLevel(logging.DEBUG)
fh = logging.FileHandler('update_info.log')
fh.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(message)s')
fh.setFormatter(formatter)
logger.addHandler(fh)

addin = "今日更新%s条，新增%s条数据，用时%s"%(update_amount,insert_amount,used_time)
logger.info(addin)
