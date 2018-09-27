import socket
import urllib.request

socket.setdefaulttimeout(5)  #设置全局超时时间
url = "http://www.baidu.com"  #打算爬取的网址

try:
    res=urllib.request.urlopen(url).read()
    print(len(res))
except:
    print("fail")

try:
    proxy_support = urllib.request.ProxyHandler({"http": "http://103.14.8.239:8080"})
    opener = urllib.request.build_opener(proxy_support)
    opener.addheaders=[("User-Agent","Mozilla/5.0 (Windows NT 10.0; WOW64)")]
    urllib.request.install_opener(opener)
    res = urllib.request.urlopen(url).read()
    print(len(res))
    print(res)
except:
    print("fail")
