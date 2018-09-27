from server.db import connection_pool
import hashlib
from unittest import TestCase, main 

COMPANY_CONN = connection_pool.get_mysql_conn('mysql_company')

class LieBrand(dict):
    brand_name = ''
    brand_desc = ''
    site_url = ''

    @classmethod
    def addLieBrand(cls, lieBrand):
        '''
        method: addBrand
        params:
            lieBrand-type: LieBrand
        '''
        global COMPANY_CONN
        cursor = None
        try:
            cursor = COMPANY_CONN.cursor(buffered=True, dictionary=True)
            sql = ("insert into lie_brand(brand_name, brand_desc, site_url)"
                   "values(%(brand_name)s, %(brand_desc)s, %(site_url)s)")
            cursor.execute(sql, lieBrand)
            COMPANY_CONN.commit()
        except Exception as e:
            print(e)
            COMPANY_CONN.rollback()
            return None
        finally:
            if cursor is not None:
                cursor.close()

    @classmethod
    def get_brand_id_by_brand_name(cls, brand_name):
        '''
        method: get_brand_id_by_brand_name
        params:
            brand_name-type: str
        return: brand_id
        return-type: int
        '''
        global COMPANY_CONN
        cursor = None
        try:
            cursor = COMPANY_CONN.cursor(buffered=True, dictionary=True)
            sql = ("select brand_id from lie_brand "
                   "where brand_name = %(brand_name)s")
            cursor.execute(sql, {'brand_name': brand_name})
            brand_id = cursor.fetchone()
            brand_id = brand_id['brand_id'] if brand_id else None
            return brand_id
        except Exception as e:
            print(e)
            return None
        finally:
            if cursor:
                cursor.close()

class LieCategory(dict):
    cat_name = ''
    brand_id = ''
    parent_id = ''
    url = ''
    level = ''
    ext_fields = ''
    islast = '' # 0 or 1

    @classmethod
    def addLieCategory(cls, lieCategory):
        '''
        method: addLieCategory
        params:
            lieCategory-type: LieCategory
        '''
        global COMPANY_CONN
        cursor = None
        try:
            cursor = COMPANY_CONN.cursor(buffered=True, dictionary=True)
            sql = ("insert into lie_category(cat_name, brand_id,"
                   "parent_id, url, level, ext_fields, islast)"
                   "values(%(cat_name)s, %(brand_id)s, %(parent_id)s, "
                   "%(url)s, %(level)s, %(ext_fields)s, %(islast)s)") 
            cursor.execute(sql, lieCategory)
            COMPANY_CONN.commit()
        except Exception as e:
            print(e)
            COMPANY_CONN.rollback()
            return None
        finally:
            if cursor is not None:
                cursor.close()

    @classmethod
    def get_cat_id_by_cat_name_brand_id(cls, cat_name, brand_id):
        '''
        method: get_cat_id_by_cat_name
        params:
            cat_name-type: str
            brand_id-type: int

        return: cat_id
        return-type: int
        '''
        global COMPANY_CONN
        cursor = None
        try:
            cursor = COMPANY_CONN.cursor(buffered=True, dictionary=True)
            sql = ("select cat_id from lie_category"
                   " where cat_name = %(cat_name)s and brand_id = %(brand_id)s")
            cursor.execute(sql, {'cat_name': cat_name, 'brand_id': brand_id})
            cat_id = cursor.fetchone()
            cat_id = cat_id['cat_id'] if cat_id else None
            return cat_id
        except Exception as e:
            print(e)
            return None
        finally:
            if cursor is not None:
                cursor.close()

    @classmethod
    def get_cat_id_by_url(cls, url):
        '''
        method: get_cat_id_by_url
        params:
            url-type: str
        return: cat_id
        return-type: int
        '''
        global COMPANY_CONN
        cursor = None
        try:
                sql = ("select cat_id from lie_category where "
                      "url = %(url)s") 
                cursor.execute(sql, {'url': url})
                cat_id = cursor.fetchone()
                cat_id = cat_id['cat_id'] if cat_id else None
                return cat_id
        except Exception as e:
            print(e)
            return None
        finally:
            if cursor is not None:
                cursor.close()

    @classmethod
    def get_all_brand_id_cat_id_url(cls):
        global COMPANY_CONN
        cursor = None
        try:
            cursor = COMPANY_CONN.cursor(buffered=True, dictionary=True)
            sql = 'select brand_id, cat_id, url from lie_category'
            cursor.execute(sql)
            all_bcu = cursor.fetchall()
            result = []
            for elem in all_bcu:
                result.append({'brand_id': elem['brand_id'],
                    'cat_id': elem['cat_id'], 'url': elem['url']})
            return result
        except Exception as e:
            print(e)
            return None
        finally:
            if cursor is not None:
                cursor.close()

class LieCategoryItems(dict):
    items_name = ''
    cat_id = ''
    brand_id = ''
    url = ''

    @classmethod
    def addLieCategoryItems(cls, lieCategoryItems):
        '''
        method: addLieCategoryItems
        params:
            lieCategoryItems-type: LieCategoryItems
        '''
        global COMPANY_CONN
        cursor = None
        try:
            cursor = COMPANY_CONN.cursor(buffered=True, dictionary=True)
            sql = ("insert into lie_category_items(items_name,"
                   "cat_id, brand_id,url) values(%(items_name)s,%(cat_id)s"
                   ",%(brand_id)s,%(url)s)")
            cursor.execute(sql, lieCategoryItems)
            COMPANY_CONN.commit()
        except Exception as e:
            print(e)
            COMPANY_CONN.rollback()
            return None
        finally:
            if cursor is not None:
                cursor.close()

    @classmethod
    def get_items_id_by_items_name(cls, items_name):
        '''
        method: get_items_id_by_items_name
        params:
            items_name-type: str

        return: items_id
        return-type: int
        '''
        global COMPANY_CONN
        cursor = None
        try:
            cursor = COMPANY_CONN.cursor(buffered=True, dictionary=True)
            sql = ("select items_id from lie_category_items where "
                   "items_name = %(items_name)s")
            cursor.execute(sql, {'items_name': items_name})
            items_id = cursor.fetchone()
            items_id = items_id['items_id'] if items_id else None
            return items_id
        except Exception as e:
            print(e)
            return None
        finally:
            if cursor is not None:
                cursor.close()

    @classmethod
    def get_cat_id_items_id_brand_id_by_url(cls, url):
        '''
        method: get_cat_id_items_id_brand_id_by_url
        params:
            url-type: str
        return-type: dict
        return: {'cat_id': 1, 'items_id': 1, 'brand_id': 1}
        '''
        global COMPANY_CONN
        cursor = None
        try:
            cursor = COMPANY_CONN.cursor(buffered=True, dictionary=True)
            sql = ("SELECT cat_id, items_id FROM lie_category_items "
                  "WHERE url = %(url)s")
            cursor.execute(sql, {'url': url})
            cib = cursor.fetchone()
            result = []
            cib = cib if cib else None
            for elem in cib:
                result.append(
                        {'cat_id': elem['cat_id'], 
                        'items_id': elem['items_id'],
                        'brand_id': elem['brand_id']})
            return result
        except Exception as e:
            print(e)
            return None
        finally:
            if cursor is not None:
                cursor.close()

    @classmethod
    def get_brand_id_cat_id_items_id_url_by_page(cls, page):
        '''
        method: get_brand_id_cat_id_iems_id_url_by_page
        params:
            page-type: int
        '''
        global COMPANY_CONN
        cursor = None
        try:
            cursor = COMPANY_CONN.cursor(buffered=True, dictionary=True)
            sql = ("SELECT brand_id, cat_id, items_id ,"
                   "url FROM lie_category_items"
                   " limit %d, 100" % ((page-1) * 100))
            cursor.execute(sql)
            bcius = cursor.fetchall()
            bcius = bcius if bcius else None
            result = []
            for elem in bcius:
                result.append({'brand_id': elem['brand_id'],
                    'cat_id': elem['cat_id'], 'items_id': elem['items_id'],
                    'url': elem['url']})
            return result
        except Exception as e:
            print(e)
            return None
        finally:
            if cursor is not None:
                cursor.close()

    @classmethod
    def get_count(cls):
        '''
        method: get_count
        return: count
        return-type:int
        '''
        global COMPANY_CONN
        cursor = None
        try:
            cursor = COMPANY_CONN.cursor(buffered=True, dictionary=True)
            sql = ("SELECT COUNT(*) as count FROM lie_category_items")
            cursor.execute(sql)
            count = cursor.fetchone()
            count =  count['count'] if count else None
            return count
        except Exception as e:
            print(e)
            return None
        finally:
            if cursor is not None:
                cursor.close()

class LieGoods(dict):
    cat_id = ''
    items_id = ''
    goods_sn = ''
    goods_name = ''
    brand_id = ''
    min_buynum = ''
    goods_desc = ''

    @classmethod
    def addLieGoods(cls, lieGoods):
        '''
        method: addLieGoods
        params:
            lieGoods-type: LieGoods
        '''
        global COMPANY_CONN
        cursor = None
        try:
            cursor = COMPANY_CONN.cursor(buffered=True, dictionary=True)
            sql =  ("INSERT INTO lie_goods"+\
                    "(cat_id, items_id, goods_sn, goods_name, brand_id,"+\
                    "min_buynum, goods_desc) "+\
                    "VALUES(%(cat_id)s, %(items_id)s, %(goods_sn)s,"
                    "%(goods_name)s, %(brand_id)s, %(min_buynum)s,"
                    "%(goods_desc)s)")
            cursor.execute(sql, lieGoods)
            COMPANY_CONN.commit()
        except Exception as e:
            print(e)
            COMPANY_CONN.rollback()
            return None
        finally:
            if cursor is not None:
                cursor.close()

    @classmethod
    def get_goods_id_by_goods_sn(cls, goods_sn_md5):
        '''
        method: get_goods_id_by_goods_sn
        params:
            goods_sn_md5-type: str
        return: goods_id
        return-type: int
        '''
        global COMPANY_CONN
        cursor = None
        try:
            cursor = COMPANY_CONN.cursor(buffered=True, dictionary=True)
            sql = ("SELECT goods_id FROM lie_goods "
                   "WHERE goods_sn = %(goods_sn)s") 
            cursor.execute(sql, {'goods_sn': goods_sn_md5})
            goods_id = cursor.fetchone()
            goods_id = goods_id['goods_id'] if goods_id else None
            return goods_id
        except Exception as e:
            print(e)
            return None
        finally:
            if cursor is not None:
                cursor.close()

class LieGoodsPrice(dict):
    goods_id = ''
    price = ''

    @classmethod
    def addLieGoodsPrice(cls, lieGoodsPrice):
        '''
        method: addLieGoodsPrice
        params:
            lieGoodsPrice-type: LieGoodsPrice
        '''
        global COMPANY_CONN
        cursor = None
        try:
            n = str(lieGoodsPrice['goods_id'])[-1:]
            cursor = COMPANY_CONN.cursor(buffered=True, dictionary=True)
            sql = ("INSERT INTO lie_goods"
                   "(goods_id, price) "
                   "VALUES(%(goods_id)s, %(price)s)")
            cursor.execute(sql, lieGoodsPrice)
            COMPANY_CONN.commit()
        except Exception as e:
            print(e)
            COMPANY_CONN.rollback()
        finally:
            if cursor is not None:
                cursor.close()

    @classmethod
    def get_price_by_goods_id(cls, goods_id):
        '''
        method: get_price_by_goods_id
        params:
            goods_id-type: int
        return: price
        return-type: str json
        '''
        global COMPANY_CONN
        cursor = None
        try:
            n = str(goods_id)[-1:]
            cursor = COMPANY_CONN.cursor(buffered=True, dictionary=True)
            sql = ("SELECT price FROM lie_goods_price_" + n + " "
                   "WHERE goods_id = %(goods_id)s")
            cursor.execute(sql, {'goods_id': goods_id})
            price = cursor.fetchone()
            price = price['price'] if price else None
            return price
        except Exception as e:
            print(e)
            return None
        finally:
            if cursor is not None:
                cursor.close()
