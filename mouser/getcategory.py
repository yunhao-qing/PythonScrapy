import requests
from lxml import etree

user_agent = "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0)"
header = {"User-Agent":user_agent}
nn_url = 'https://products.avnet.com/shop/AllProducts?catalogId=10001&langId=-7&storeId=715839038'
try:
    r = requests.get(nn_url, headers=header,timeout = 30)
    r.encoding = 'utf-8'
    content = r.text
    et = etree.HTML(content)
    lis = et.xpath('//li[@class="pdt_expand"]')
    for i in lis:
        t = i.xpath("./a/text()")
        link=i.xpath("./a/@href")
        print("一级分类:"+str(t))
        print(link)
        sublis=i.xpath('./ul/li')
        for subli in sublis:
            sub=subli.xpath("./a/text()")
            link = subli.xpath("./a/@href")
            print("二级分类:"+str(sub))
            print(link)
except:
    print("what")

