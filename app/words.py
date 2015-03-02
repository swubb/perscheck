import re

ins = open( "static/woordenlijst.txt", "r" )
dict = {}
vervang={}
for line in ins:
   	fields = line.rstrip().split(" 1" )
   	if len(fields)>1:
   		dict[fields[0]]="1"+fields[1]
ins.close()

line ="sanctioneren derka derka schrijven repliceren brief bla bla bla kabouter koek aap "

for i in dict:
	
	if re.search(i, line) :
		print i, dict[i]
		vervang[i] = dict[i]


print vervang