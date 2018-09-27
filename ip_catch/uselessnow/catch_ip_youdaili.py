import requests
import re

url = "http://www.youdaili.net/Daili/guonei/"

user_agent = "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0)"
header = {"User-Agent": user_agent}

count=0
r = requests.get(url, headers=header)
r.encoding = 'utf-8'
html = r.text
pattern = re.compile(r'http://www.youdaili.net/Daili/guonei/\d\d\d\d\d.html')
items = re.findall(pattern,html)
for item in items:
    print (item)
    count=count+1

print (count)
