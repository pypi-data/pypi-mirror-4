'''def  method head  can include deep items,
the_list is the foreach list,tab_num is the level print tab num'''
def print_lol(the_list,indent=False,tab_num=0):
	'''define method body ,for each print or callback method'''	
	for each_item in the_list:
		if isinstance(each_item,list):
			print_lol(each_item,indent,tab_num+1)
		else:
			for num in range(tab_num):
				if indent:
					print("\t",end="")
			print(each_item)
