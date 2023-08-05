import http.client
fp = open("./list","r")
lines = fp.readlines()
for item in lines:
	print(item,end='')
	length = len(item)
	newstr = item[0:length-1]
	conn = http.client.HTTPConnection(newstr)
	conn.request("GET","")
	r1 = conn.getresponse()
	print(r1.status,r1.reason)
