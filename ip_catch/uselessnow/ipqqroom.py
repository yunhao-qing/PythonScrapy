import re
import requests

url="http://ip.qqroom.cn/"
r = requests.get(url)
r.encoding = 'utf-8'
html = r.text
pattern="http:///d+/./d+/./d+/./d/:/d"
m = re.search(pattern,html)
print(m.group())
