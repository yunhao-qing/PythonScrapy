import time
import mysql.connector

filename = "F://12345.json"
f = open(filename,encoding='utf-8')
lines = f.readlines()

goods_sn=[]

for line in lines:
    sn=line.split("'goods_sn': '")[1].split("', 'goods_name")[0]
    goods_sn.append(sn)

print(goods_sn)









