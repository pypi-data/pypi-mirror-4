'''A function to print nested lists'''

def print_lol(my_list):
	for item in my_list:
		if isinstance(item,list):
			print_lol(item)
		else:
			print(item)