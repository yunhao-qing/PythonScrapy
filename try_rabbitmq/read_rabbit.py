import urllib.request

password_mgr = urllib.request.HTTPPasswordMgrWithDefaultRealm()

top_level_url = "http://192.168.1.88:15672/api/queues?page=1&page_size=100&name=&use_regex=false"
username = "admin"
password = "123456"

password_mgr.add_password(None, top_level_url, username, password)
handler = urllib.request.HTTPBasicAuthHandler(password_mgr)
opener = urllib.request.build_opener(handler)
opener.open(top_level_url)
urllib.request.install_opener(opener)

a=urllib.request.urlopen(top_level_url).read().decode()
a = a.replace('null', "''")
a = a.replace('false', "False")
a = a.replace('true', "True")
splited=a.split('{"memory"')
splited=splited[1:]
splited[-1]=splited[-1][:-1]
for i in range(len(splited)):
    data_string=str('{"memory"'+splited[i][:-1])
    data_dict=eval(data_string)
    if type(data_dict)==tuple:
        data_dict=data_dict[0]
    print("____________________")
    print('名称：'+str(data_dict["name"]))
    print('messages_ready：'+str(data_dict["messages_ready"]))
    print('messages_unask：'+str(data_dict["messages_unacknowledged"]))
    print('messages：'+str(data_dict["messages"]))

