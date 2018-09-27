import requests

user_agent = "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0)"
header = {"User-Agent":user_agent}
nn_url = 'https://products.avnet.com/shop/en/ema/rf-and-microwave/vcos'
r = requests.get(nn_url, headers=header,timeout = 30)
print(r.text)