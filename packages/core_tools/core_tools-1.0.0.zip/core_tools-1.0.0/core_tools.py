'''def  method head  can include deep items'''
def print_lol(the_list):
	'''define method body ,for each print or callback method'''	
	for each_item in the_list:
		if isinstance(each_item,list):
			print_lol(each_item)
		else:
			print(each_item)
