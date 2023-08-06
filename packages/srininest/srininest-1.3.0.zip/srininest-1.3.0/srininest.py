def print_number(mylist,indent=False,level=0):
	for each_member in mylist:
		if isinstance(each_member,list):
			print_number(each_member,indent,level+1)
		else :
                        if indent:
                                for everything in range(level):
                                        print("\t",end='')
                                print(each_member)
