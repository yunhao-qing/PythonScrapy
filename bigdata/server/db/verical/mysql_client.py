from server.db import connection_pool
import traceback

VERICAL_CONN = connection_pool.get_mysql_conn('mysql_verical')

class LieBrand(dict):
    brand_name = ''
    brand_logo = ''
    brand_desc = ''
    site_url = ''
    web_url = ''
    sort_order = ''
    is_show = ''

    @classmethod
    def addLieBrand(cls, lieBrand):
        '''
        method: addLieBrand
        params:
            lieBrand-type: LieBrand
        '''
        global VERICAL_CONN
        cursor = None
        try:
            cursor = VERICAL_CONN.cursor(buffered=True, dictionary=True)
            sql = ("insert into lie_brand(brand_name, brand_logo, brand_desc,"
                    "site_url, web_url) "
                    "values(%(brand_name)s,%(brand_logo)s,%(brand_desc)s,"
                    "%(site_url)s, %(web_url)s)")
            cursor.execute(sql, lieBrand)
        except Exception as e:
            print(e)
        finally:
            if cursor:
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
        global VERICAL_CONN
        cursor = None
        try:
            cursor = VERICAL_CONN.cursor(buffered=True, dictionary=True)
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
    keywords = ''
    cat_desc = ''
    parent_id = ''
    sort_order = '50'
    is_show = '1'
    url = ''
    ext_fields = ''
    recom_attr = ''
    islast = ''
    level = ''
    page_count = '' # 待加关键字 总页数

    @classmethod
    def addLieCategory(cls, lieCategory):
        '''
        method: addLieCategory
        params:
            lieCategory-type: LieCategory
        '''
        global VERICAL_CONN
        cursor = None
        try:
            cursor = VERICAL_CONN.cursor(buffered=True, dictionary=True)
            sql = ("insert into lie_category"
                    "(cat_name, "
                    " keywords, "
                    " cat_desc, "
                    " parent_id,"
                    " sort_order, " 
                    " is_show, "
                    " url, " 
                    " ext_fields, "
                    " recom_attr, "
                    " islast, "
                    " level, "
                    " page_count)"
                    " " 
                    " values("
                    " %(cat_name)s, "
                    " %(keywords)s, "
                    " %(cat_desc)s, "
                    " %(parent_id)s," 
                    " %(sort_order)s, " 
                    " %(is_show)s, "
                    " %(url)s, "
                    " %(ext_fields)s, "
                    " %(recom_attr)s, "
                    " %(islast)s, "
                    " %(level)s, "
                    " %(page_count)s)")
            cursor.execute(sql, lieCategory)
        except Exception as e:
            print(e)
        finally:
            if cursor:
                cursor.close()

    @classmethod
    def get_cat_id_by_cat_name(cls, cat_name):
        '''
        method: get_cat_id_by_cat_name
        params:
            cat_name-type: str
        return: cat_id
        return-type: int
        '''
        global VERICAL_CONN
        cursor = None
        try:
            cursor = VERICAL_CONN.cursor(buffered=True, dictionary=True)
            sql = ("select cat_id from lie_category "
                    "where cat_name = %(cat_name)s")
            cursor.execute(sql, {'cat_name': cat_name})
            cat_id = cursor.fetchone()
            cat_id = cat_id['cat_id'] if cat_id else None
            return cat_id
        except Exception as e:
            print(e)
            return None
        finally:
            if cursor:
                cursor.close()

    @classmethod
    def get_all_cat_id_url_page_count(cls):
        '''
        method: get_all_cat_id_url_page_count
        return: {'cat_id': 1, 'url': 'adf.com', 'page_count': 1}
        '''
        global VERICAL_CONN
        cursor = None
        try:
            cursor = VERICAL_CONN.cursor(buffered=True, dictionary=True)
            sql = ("select cat_id, url, page_count from lie_category "
                    "where parent_id != 0")
            cursor.execute(sql)
            result = cursor.fetchall()
            cups = []
            for row in result:
                cups.append(row)
            return cups
        except Exception as e:
            print(e)
            return None
        finally:
            if cursor:
                cursor.close()
    
    @classmethod
    def get_all_cat_id_url_page_count_by_page(cls, page):
        '''
        method: get_all_cat_id_url_page_count_by_page
        params:
            page-type: int
        return-type: [
            {'cat_id': 1, 'url': 'http://baidu.com', 'page_count': 28},..., n]    
        '''
        global VERICAL_CONN
        cursor = None
        try:
            cursor = VERICAL_CONN.cursor(buffered=True, dictionary=True)
            sql = ("select cat_id, url, page_count from lie_category "
                    "where parent_id != 0 limit " + str((page-1)*100) + ", 100")
            cursor.execute(sql)
            result = cursor.fetchall()
            cups = []
            for row in result:
                cups.append(row)
            return cups
        except Exception as e:
            print(e)
            return None
        finally:
            if cursor:
                cursor.close()

    @classmethod
    def update_lie_category_page_count_by_cat_id(cls, cat_id, page_count):
        '''
        method: update_lie_category_page_count_by_cat_id
        params:
            cat_id-type: int
            page_count-type: int
        '''
        global VERICAL_CONN
        cursor = None
        try:
            cursor = VERICAL_CONN.cursor(buffered=True, dictionary=True)
            sql = ("update lie_category set page_count = %(page_count)s "
                    "where cat_id = %(cat_id)s")
            args = dict(cat_id=cat_id, page_count=page_count)
            cursor.execute(sql, args)
        except Exception as e:
            print(e)
        finally:
            if cursor:
                cursor.close()

    @classmethod
    def get_count(cls):
        '''
        method: get_count
        return: count
        return-type: int
        '''
        global VERICAL_CONN
        cursor = None
        try:
            cursor = VERICAL_CONN.cursor(buffered=True, dictionary=True)
            sql = ("select count(*) as count from lie_category "
                    "where parent_id != 0")
            cursor.execute(sql)
            result = cursor.fetchone()
            count = result['count'] if result else None
            return count
        except Exception as e:
            print(e)
            return None
        finally:
            if cursor:
                cursor.close()

    @classmethod
    def get_all_cat_id_keywords(cls):
        global VERICAL_CONN
        cursor = None
        try:
            cursor = VERICAL_CONN.cursor(buffered=True, dictionary=True)
            sql = ("select cat_id, keywords from lie_category where islast=1 ")
            cursor.execute(sql)
            result = cursor.fetchall()
            cks = []
            for row in result:
                cks.append(row)
            return cks
        except Exception as e:
            print(e)
            return None
        finally:
            if cursor:
                cursor.close()

    @classmethod
    def get_all_cat_id_keywords_page_count(cls):
        global VERICAL_CONN
        cursor = None
        try:
            cursor = VERICAL_CONN.cursor(buffered=True, dictionary=True)
            sql = ("select cat_id, keywords, page_count from lie_category "
                    "where islast=1")
            cursor.execute(sql)
            result = cursor.fetchall()
            ckps = []
            for row in result:
                ckps.append(row)
            return ckps
        except Exception as e:
            print(e)
            return None
        finally:
            if cursor:
                cursor.close()

class LieGoods(dict):
    cat_id = ''
    goods_sn = ''
    goods_name = ''
    goods_name_style = ''
    brand_id = ''
    provider_name = ''
    pdf_url = ''
    goods_number = ''
    shop_price = ''
    min_buynum = ''
    goods_brief = ''
    goods_desc = ''
    goods_thumb = ''
    goods_img = ''
    is_on_sale = ''
    add_time = ''
    sort_order = ''
    is_delete = ''
    last_update = ''
    is_check = ''
    site_url = ''
    series = ''
    is_rohs = ''
    is_insert = ''
    warehouse = ''
    Encap = ''
    Package = ''
    MOQ = ''
    SPQ = ''
    HDT = ''
    CDT = ''
    increment = ''

    @classmethod
    def addLieGoods(cls, lieGoods):
        '''
        method: addLieGoods
        params:
            lieGoods-type: LieGoods
        '''
        global VERICAL_CONN
        cursor = None
        try:
            cursor = VERICAL_CONN.cursor(buffered=True, dictionary=True)
            sql = ("insert into lie_goods("
                    "cat_id, "
                    "goods_sn, "
                    "goods_name,"
                    "provider_name, "
                    "pdf_url,"
                    "min_buynum, "
                    "goods_brief,"
                    "goods_desc, "
                    "goods_thumb, "
                    "goods_img, "
                    "site_url, "
                    "series, "
                    "warehouse,"
                    "Encap, "
                    "Package, "
                    "HDT, "
                    "CDT, "
                    "goods_name_style, "
                    "is_check) "
                    " "
                    "values("
                    "%(cat_id)s,"
                    "%(goods_sn)s, "
                    "%(goods_name)s, "
                    "%(provider_name)s, "
                    "%(pdf_url)s,"
                    "%(min_buynum)s,"
                    "%(goods_brief)s, "
                    "%(goods_desc)s, "
                    "%(goods_thumb)s,"
                    "%(goods_img)s, "
                    "%(site_url)s, "
                    "%(series)s, "
                    "%(warehouse)s, "
                    "%(Encap)s, "
                    "%(Package)s,"
                    "%(HDT)s, "
                    "%(CDT)s, "
                    "%(goods_name_style)s, "
                    "%(is_check)s)")
            lieGoods['is_check'] = 0
            cursor.execute(sql, lieGoods)
        except Exception as e:
            print(e)
            exstr = traceback.format_exc()
            print(exstr)

        finally:
            if cursor:
                cursor.close()
    
    @classmethod
    def get_goods_id_by_goods_sn(cls, goods_sn):
        '''
        method: get_goods_id_by_goods_sn
        params:
            goods_sn-type: str 
        return: goods_id
        return-type: int
        '''
        global VERICAL_CONN
        cursor = None
        try:
            cursor = VERICAL_CONN.cursor(buffered=True, dictionary=True)
            sql = ("select goods_id from lie_goods where goods_sn = %(goods_sn)s")
            cursor.execute(sql, {'goods_sn': goods_sn})
            goods_id = cursor.fetchone()
            goods_id = goods_id['goods_id'] if goods_id else None
            return goods_id
        except Exception as e:
            print(e)
            exstr = traceback.format_exc()
            print(exstr)

            return None
        finally:
            if cursor:
                cursor.close()

    @classmethod
    def get_goods_by_goods_sn(cls, goods_sn):
        global VERICAL_CONN
        cursor = None
        try:
            cursor = VERICAL_CONN.cursor(buffered=True, dictionary=True)
            sql = ("select * "
                    "from lie_goods where goods_sn = %(goods_sn)s")
            cursor.execute(sql, {'goods_sn': goods_sn})
            g = cursor.fetchone()
            return g
        except Exception as e:
            print(e)
            exstr = traceback.format_exc()
            print(exstr)

            return None
        finally:
            if cursor:
                cursor.close()

    @classmethod
    def get_count(cls):
        '''
        method: get_count
        return: count
        return-type: int
        '''
        global VERICAL_CONN
        cursor = None
        try:
            cursor = VERICAL_CONN.cursor(buffered=True, dictionary=True)
            sql = ("select count(*) as count from lie_goods")
            cursor.execute(sql)
            result = cursor.fetchone()
            count = result['count']
            return count
        except Exception as e:
            print(e)
            exstr = traceback.format_exc()
            print(exstr)

            return None
        finally:
            if cursor:
                cursor.close()

    @classmethod
    def get_cat_id_goods_id_goods_name_goods_sn_site_url_pdf_url_by_page(cls, 
            goods_id):
        global VERICAL_CONN
        cursor = None
        try:
            cursor = VERICAL_CONN.cursor(buffered=True, dictionary=True)
            sql = ("select cat_id, goods_id, goods_name, goods_sn, site_url, "
                    "pdf_url from lie_goods "
                    "where goods_id >= %(goods_id)s order by goods_id asc "
                    "limit 100")
            cursor.execute(sql, {'goods_id': goods_id})
            result = cursor.fetchall()
            cggups = []
            for row in result:
                cggups.append(row)
            return cggups
        except Exception as e:
            print(e)
            exstr = traceback.format_exc()
            print(exstr)

            return None
        finally:
            if cursor:
                cursor.close()

    @classmethod
    def get_first_goods_id(cls):
        global VERICAL_CONN
        cursor = None
        try:
            cursor = VERICAL_CONN.cursor(buffered=True, dictionary=True)
            sql = ("select goods_id from lie_goods order by goods_id asc limit 1")
            cursor.execute(sql)
            result = cursor.fetchone()
            goods_id = result['goods_id']
            return goods_id
        except Exception as e:
            print(e)
            exstr = traceback.format_exc()
            print(exstr)

            return None
        finally:
            if cursor:
                cursor.close()

    @classmethod
    def get_last_goods_id(cls):
        global VERICAL_CONN
        cursor = None
        try:
            cursor = VERICAL_CONN.cursor(buffered=True, dictionary=True)
            sql = ("select goods_id from lie_goods order by goods_id desc limit 1")
            cursor.execute(sql)
            result = cursor.fetchone()
            goods_id = result['goods_id']
            return goods_id
        except Exception as e:
            print(e)
            exstr = traceback.format_exc()
            print(exstr)

            return None
        finally:
            if cursor:
                cursor.close()

    @classmethod
    def update_goods(cls, lieGoods):
        global VERICAL_CONN
        cursor = None
        try:
            cursor = VERICAL_CONN.cursor(buffered=True, dictionary=True)
            sql = ("update lie_goods set "
                    "provider_name=%(provider_name)s, "
                    "goods_desc=%(goods_desc)s, "
                    "goods_name_style=%(goods_name_style)s, "
                    "brand_Id=%(brand_id)s, "
                    "site_url=%(site_url)s "
                   "where goods_id=%(goods_id)s")
            cursor.execute(sql, lieGoods)
        except Exception as e:
            exstr = traceback.format_exc()
            print(exstr)

            print(e)
        finally:
            if cursor:
                cursor.close()

    @classmethod
    def get_goods_name_style_by_goods_sn(cls, goods_sn):
        global VERICAL_CONN
        cursor = None
        try:
            cursor = VERICAL_CONN.cursor(buffered=True, dictionary=True)
            sql = ("select goods_name_style from lie_goods where "
                    "goods_sn=%(goods_sn)s")
            cursor.execute(sql, {'goods_sn': goods_sn})
            result = cursor.fetchone()
            gns = result['goods_name_style'] if result else None
            return gns
        except Exception as e:
            print(e)
            exstr = traceback.format_exc()
            print(exstr)

            return None

        finally:
            if cursor:
                cursor.close()

class LieGoodsPrice(dict):
    goods_id = ''
    price = ''

    @classmethod
    def addLieGoodsPrice(cls, lieGoodsPrice):
        global VERICAL_CONN
        cursor = None
        try:
            goods_id = lieGoodsPrice['goods_id']
            n = str(goods_id)[-1:]
            cursor = VERICAL_CONN.cursor(buffered=True, dictionary=True)
            sql = ("insert into lie_goods_price_"+ n +"(goods_id, price) "
                    "values(%(goods_id)s, %(price)s)")
            cursor.execute(sql, lieGoodsPrice)
        except Exception as e:
            print(e)
            exstr = traceback.format_exc()
            print(exstr)
        finally:
            if cursor:
                cursor.close()

    @classmethod
    def exist(cls, goods_id):
        global VERICAL_CONN
        cursor = None
        try:
            n = str(goods_id)[-1:]
            cursor = VERICAL_CONN.cursor(buffered=True, dictionary=True)
            sql = ("select goods_id from lie_goods_price_" + n + " "
                    "where goods_id = %(goods_id)s")
            cursor.execute(sql, {'goods_id': goods_id})
            result = cursor.fetchone()
            goods_id = result['goods_id'] if result else None
            return goods_id
        except Exception as e:
            print(e)
            exstr = traceback.format_exc()
            print(exstr)
            return None
        finally:
            if cursor:
                cursor.close()

if __name__ == '__main__':
    LieGoods.del_goods_like_goods_sn('%€€%[_]_[_]_')
    VERICAL_CONN.close()
