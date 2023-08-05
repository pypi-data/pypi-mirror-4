def listlooper(a_list, level=0, indent=false):
	for each_item in a_list:
		if isinstance(each_item, list):
			listlooper(each_item, level+1, indent)
		else:
                        if indent:
                                for total_tabs in range(level):
                                                print("\t", end=" ")
                        print(each_item)

names = ['John', 'Eric', ['Cleese', 'Idle'], 'Michael', ['Palin']]


		
