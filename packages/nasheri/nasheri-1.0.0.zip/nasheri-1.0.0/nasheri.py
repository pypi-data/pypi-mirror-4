"""hello python"""
def nasheri(tlist):
	for each_person in tlist:
		if isinstance(each_person,list):
			nasheri(each_person)
		else:
			print(each_person)
print("bye")
