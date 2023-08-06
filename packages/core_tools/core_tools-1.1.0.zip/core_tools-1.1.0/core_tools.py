'''def  method head  can include deep items,
the_list is the foreach list,tab_num is the level print tab num'''
def print_lol(the_list,tab_num):
	'''define method body ,for each print or callback method'''	
	for each_item in the_list:
		if isinstance(each_item,list):
			print_lol(each_item,tab_num+1)
		else:
			for num in range(tab_num):
				print("\t",end="")
			print(each_item)
