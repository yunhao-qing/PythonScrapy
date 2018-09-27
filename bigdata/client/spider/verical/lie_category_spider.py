from lxml import etree
import requests
from client.spider.base import Spider
import logging
import webbrowser

class LieCategorySpider(Spider):
    def __init__(self):
        Spider.__init__(self)
        self.url = 'https://static.verical.com/prod/generated/master.json'
        self.headers = {
            'User-Agent': 'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.2; SV1; .NET CLR 1.1.4322)',
        }



    def get_all_categories(self):
        return self.get_no_proxies(self.url, headers=self.headers, timeout=30)

    def parse_get_all_categories(self, html):
        if html is None:
            return 
        base_url = 'https://www.verical.com'

        html = html.replace('null', "''")
        html = html.replace('false', "False")
        html = html.replace('true', "True")

        d = eval(html)
        categoryTree = d['categoryTree']
        categories = categoryTree['categories']

        result = []
        for lc_0 in categories:
            lc_0_name = lc_0['name']
            lc_0_parent_id = 0
            lc_0_level = 0
            lc_0_categories = lc_0['categories']

            lc_0_dict = dict()
            lc_0_dict['cat_name'] = lc_0_name
            lc_0_dict['parent_id'] = 0
            lc_0_dict['level'] = lc_0_level
            lc_0_dict['keywords'] = lc_0['id']
            lc_0_dict['islast'] = 0
            lc_0_dict['cat_desc'] = ''
            lc_0_dict['sort_order'] = 50
            lc_0_dict['is_show'] = 1
            lc_0_dict['ext_fields'] = ''
            lc_0_dict['recom_attr'] = ''
            lc_0_dict['page_count'] = 1

            if lc_0_name == 'Others':
                lc_0_dict['url'] = base_url + '/products/miscellaneous-100x000/' + \
                        lc_0_name.replace(' ','-').replace('&', '%26').\
                        replace(',','').lower() +\
                        '-' + str(lc_0['privateId']) + '/'
                lc_0_dict['islast'] = 1
            else:
                lc_0_dict['url'] = base_url + '/products/%s-%d/' % (
                        lc_0_name.replace(' ','-').replace('&', '%26').\
                        replace(',','').replace('/','-').lower(),
                        lc_0['privateId'])

            lc_0_dict['sub_categories'] = []
            result.append(lc_0_dict)

            for lc_1 in lc_0_categories:
                lc_1_name = lc_1['name']
                lc_1_parent_id = lc_0_name
                lc_1_level = 1
                lc_1_categories = lc_1['categories']
                lc_1_dict = {
                    'cat_name': lc_1_name,
                    'parent_id': lc_1_parent_id,
                    'level': lc_1_level,
                    'sub_categories': []      
                }
                lc_1_dict['keywords'] = lc_1['id']
                lc_1_dict['islast'] = 0
                lc_1_dict['cat_desc'] = ''
                lc_1_dict['sort_order'] = 50
                lc_1_dict['is_show'] = 1
                lc_1_dict['ext_fields'] = ''
                lc_1_dict['recom_attr'] = ''
                lc_1_dict['page_count'] = 1

                lc_1_dict['url'] = self.fz_url(lc_0_dict, lc_1_name, 
                        lc_1['privateId'])

                lc_0_dict['sub_categories'].append(lc_1_dict)

                for lc_2 in lc_1_categories:
                    lc_2_name = lc_2['name']
                    lc_2_parent_id = lc_1_name
                    lc_2_level = 2
                    lc_2_categories = lc_2['categories']
                    lc_2_dict = {
                        'cat_name': lc_2_name,
                        'parent_id': lc_2_parent_id,
                        'level': lc_2_level,
                        'sub_categories': []      
                    }
                    lc_2_dict['keywords'] = lc_2['id']
                    lc_2_dict['islast'] = 1
                    lc_2_dict['cat_desc'] = ''
                    lc_2_dict['sort_order'] = 50
                    lc_2_dict['is_show'] = 1
                    lc_2_dict['ext_fields'] = ''
                    lc_2_dict['recom_attr'] = ''
                    lc_2_dict['page_count'] = 1

                    lc_2_dict['url'] = self.fz_url(lc_1_dict, lc_2_name, 
                            lc_2['privateId'])
                    lc_1_dict['sub_categories'].append(lc_2_dict)

        return result

    def fz_url(self, lc_n_dict, name, privateId):
        tmp = lc_n_dict['url']
        tmp1 = name.lower()
        tmp1 = tmp1.replace(' - ', '-')
        tmp1 = tmp1.replace(' -', '-')
        tmp1 = tmp1.replace('- ', '-')
        tmp1 = tmp1.replace(' / ', '-')
        tmp1 = tmp1.replace(' /', '-')
        tmp1 = tmp1.replace('/ ', '-')
        tmp1 = tmp1.replace('/', '-')
        tmp1 = tmp1.replace(', ', '-')
        tmp1 = tmp1.replace('&', '%26')

        tmp1 = '-'.join(tmp1.lower().split(' '))
        result = tmp + '%s-%s' % (tmp1, privateId) + '/'
        result = result.replace('---','-')
        return result

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    lc = LieCategorySpider()
    html = lc.get_all_categories()
    categories = lc.parse_get_all_categories(html)
    import pprint
    pprint.pprint(categories)
