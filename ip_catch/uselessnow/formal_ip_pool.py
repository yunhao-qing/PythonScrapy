f = open('proxy_ip.txt', 'r')
f2 = open('formal.txt', 'w')
result = list()
for line in open('proxy_ip.txt'):
    line = f.readline().strip()
    result.append(line)

formal = list(set(result))

for i in formal:
    f2.write(str(i))
    f2.write("\n")

f.close()
f2.close()