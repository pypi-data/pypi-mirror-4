'''A function to print nested lists'''

def print_lol(my_list, level=0):
	for item in my_list:
		if isinstance(item,list):
			lol(item,level+1)
		else:
			for n in range(level):
				print("\t",end='')
			print(item)
