"""hello python"""
def nasheri(tlist,level):
	for each_person in tlist:
		if isinstance(each_person,list):
			nasheri(each_person,level+1)
		else:
                      for tab_stop in range(level):
                              print("\t",end='')
		      print(each_person)
print("bye")
