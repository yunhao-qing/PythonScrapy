import pymongo

connection=pymongo.MongoClient('192.168.1.88',27017)
db=connection.ichunt
ip_list = db.ips


count=0
for item in ip_list.find():
    count=count+1

print(count)