# coding:utf-8
import requests
from lxml import etree
import time

time1 = time.time()
user_agent = "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0)"
header = {"User-Agent":user_agent}

url='https://list.jd.com/list.html?cat=670,677,681'
r = requests.get(url, headers=header,timeout = 30)
content = r.text
et = etree.HTML(content)
total_page_number=int(str(et.xpath('//span [@class="p-skip"]/em/b/text()'))[2:-2])
print(total_page_number)

scan_usls_list=[]
for i in range(1,total_page_number+1):
    url=str("https://list.jd.com/list.html?cat=670,677,681&page="
    +str(i)+"&sort=sort_totalsales15_desc&trans=1&JL=6_0_0#J_main")
    scan_usls_list.append(url)

for i in range(len(scan_usls_list)):
    url = scan_usls_list[i]
    r = requests.get(url, headers=header, timeout=30)
    content = r.text
    et = etree.HTML(content)
    lis = et.xpath('//div [@class="goods-list-v2 J-goods-list gl-type-1 "]/ul/li[@class="gl-item"]')
    for li in lis:
        div=li.xpath('./div[@class="gl-i-wrap"]')
        if div:
            div=div[0]
            div=div.xpath('./div[@class="gl-i-tab"]')[0]
            div = div.xpath('./div[@class="gl-i-tab-content"]')[0]
            div = div.xpath('./div[@class="tab-content-item tab-cnt-i-selected j-sku-item"]')[0]
            name = div.xpath('./div[@class="p-name"]/a/em/text()')[0]
            url="https:"+div.xpath('./div[@class="p-name"]/a/@href')[0]
            print("------------------------------------------")
            print("产品名："+name)
            print("url："+url)
            r = requests.get(url, headers=header, timeout=30)
            content = r.text
            try:
                content = content.split("适用CPU接口：")[1]
                cpu=content.split("</li>")[0]
            except:
                cpu="没有标注"
            print("适用CPU接口："+cpu)
            id=url.split('item.jd.com/')[1]
            id=id.split('.ht')[0]
            url = "https://p.3.cn/prices/mgets?callback=jQuery401628&type=1&area=1_72_4137_0&pdtk=&" \
                        "pduid=1330043050&pdpin=&pdbp=0&skuIds=J_" + id
            r = requests.get(url, headers=header, timeout=30)
            content = r.text.split('"p":"')[1].split('","m')[0]
            print("价格："+content)
            print("")
        else:
            div =li.xpath('./div[@class="gl-i-wrap j-sku-item"]')[0]
            name=div.xpath('./div[@class="p-name"]/a/em/text()')[0]
            url="https:"+div.xpath('./div[@class="p-name"]/a/@href')[0]
            print("------------------------------------------")
            print("产品名："+name)
            print("url："+url)
            r = requests.get(url, headers=header, timeout=30)
            content = r.text
            try:
                content = content.split("适用CPU接口：")[1]
                cpu=content.split("</li>")[0]
            except:
                cpu="没有标注"
            print("适用CPU接口："+cpu)
            id=url.split('item.jd.com/')[1]
            id=id.split('.ht')[0]
            url = "https://p.3.cn/prices/mgets?callback=jQuery401628&type=1&area=1_72_4137_0&pdtk=&" \
                        "pduid=1330043050&pdpin=&pdbp=0&skuIds=J_" + id
            r = requests.get(url, headers=header, timeout=30)
            content = r.text.split('"p":"')[1].split('","m')[0]
            print("价格："+content)

time2 = time.time()
print(time2-time1)

