'''A function to print nested lists'''

def print_lol(my_list,indent=False,level=0):
	for item in my_list:
		if isinstance(item,list):
			print_lol(item,indent,level+1)
		else:
                        if indent:
                                for n in range(level):
                                        print("\t",end='')
                        print(item)




