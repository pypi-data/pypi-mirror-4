def print_fun(the_list,indent=False,level=0):
        """这是一个python模块"""
        for each_item in the_list:
                if isinstance(each_item,list):
                        print_fun(each_item,indent,level+1)
                else:
                        if indent:
                                for t_2 in range(level):
                                        print("\t",end='')
                        print(each_item)
			

		
