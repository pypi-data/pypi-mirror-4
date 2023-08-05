def printlist(the_list):
	for each_item in the_list:
		if isinstance(each_item,list):
			printlist(each_item)
		else:
			print(each_item)

			
