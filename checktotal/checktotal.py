# coding:utf-8

"""f = open('C:/Users/Administrator/PycharmProjects/checktotal/checktotal', 'r')
count=0
for line in f.readlines():
    num=line.split(" ")[1]
    count+=int(num)
f.close()
print(count)"""

import mysql.connector

cnx = mysql.connector.connect(user='ichunt', password='ichunt',
                              host='db1.ichunt.com',port='3306',
                              database='rs',
                              use_pure=False)
cursor = cnx.cursor()


query = ("SELECT cat_id FROM lie_goods "
         "WHERE is_check=0")


cursor.execute(query)
nums=[]
for (cat_id) in cursor:
  nums.append(int(cat_id[0]))
i =1
varcount=1
while i<len(nums):
    if nums[i]==nums[i-1]:
        varcount+=1
        i+=1
    else:
        print(nums[i-1]," ",varcount)
        varcount=1
        i+=1





cursor.close()
cnx.close()