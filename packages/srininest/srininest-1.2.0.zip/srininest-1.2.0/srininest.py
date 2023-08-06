def print_number(mylist,level=0):
	for each_member in mylist:
		if isinstance(each_member,list):
			print_number(each_member,level+1)
		else :
                        for everything in range(level):
                                print("\t",end='')
                        print(each_member)
