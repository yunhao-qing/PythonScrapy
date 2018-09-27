import mysql.connector
from lxml import etree

cnx = mysql.connector.connect(user = 'ichunt', password = 'ichunt',
                              host = '192.168.1.88',
                              database = 'mouser')
cursor = cnx.cursor()

add_goods = ("INSERT INTO lie_brand (brand_name,site_url,brand_logo)  "
             "VALUES (%s,%s,%s)")

file_object = open('brands.txt')
try:
     text = file_object.read( )
     tree = etree.HTML(text)
     names=tree.xpath("//table/tr/td/a/text()")
     hrefs=tree.xpath("//table/tr/td/a/@href")
     names=names[2:]
     hrefs=hrefs[2:]
     size=len(hrefs)
     for i in range(0,size):
         b=str(names[i]).strip()
         print(b)
         if b!="JRC / NJR (New Japan Radio)":
             c="http://www.mouser.cn"+hrefs[i]
             print(c)
             a=hrefs[i]
             n=a[1:-1]
             final="http://www.mouser.cn/images/suppliers/logos/"+n+".png"
             print(final)
             data_goods = (b,c,final)
             cursor.execute(add_goods, data_goods)
             cnx.commit()
         else:
             print("stupif")
finally:
     file_object.close( )
     cursor.close()
     cnx.close()
