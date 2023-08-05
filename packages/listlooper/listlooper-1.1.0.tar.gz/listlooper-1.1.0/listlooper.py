def listlooper(a_list, level=0):
	for each_item in a_list:
		if isinstance(each_item, list):
			listlooper(each_item, level+1)
		else:
			for total_tabs in range(level):
				print("\t", end=" ")
			print(each_item)

		
