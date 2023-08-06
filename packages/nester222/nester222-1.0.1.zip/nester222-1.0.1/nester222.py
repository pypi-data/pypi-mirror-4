def print_fun(the_list,level):
	"""这是一个python模块"""
	for each_item in the_list:
		if isinstance(each_item,list):
			print_fun(each_item,level+1)
		else:
			print(each_item)

		
