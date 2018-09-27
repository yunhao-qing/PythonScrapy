# -*- coding: utf-8 -*-
import re
import time

f = open("C:/Users/Administrator/Desktop/0313.log", "r")#在此放入日志
arr = {}#创建字典
num = '\\b([1-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\\b'#1-255的字符库
lines = f.readlines()

for line in lines:
    pattern = re.compile(r'(' + num + '\.){3}' + num) #ip格式
    match = pattern.match(line)
    if match:
        ip = match.group()
    if (arr.has_key(ip)):
        arr[ip] += 1
    else:
        arr[ip] = 1
f.close()

numList = list(set(arr.values())) #去重
numList.sort(reverse=True)#逆向排序

filename="C:/Users/Administrator/Desktop/ip_track.txt" #存储文件名
record = open(filename,"w")
date=time.strftime("%d/%m/%Y") #日期
record.write(date)
record.write("\n")

for ipNum in numList:
    for ip in arr:
        if (ipNum == arr[ip]):
            record.write(ip + "--->" + str(arr[ip]))
            record.write("\n")
record.close()