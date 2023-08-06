def print_nester(the_list,level=0):
	for each_item in the_list:
		if isinstance(each_item,list):
			print_nester(each_item,level+1)
		else:
                        for tab_stop in range(level):
                                print("\t",end='')
                        print(each_item)
