"""
This function is used to parse list.
"""

def print_list (the_list,indent=False,level=0):
	for item in the_list:
		if isinstance(item, list):
			print_list(item,indent,level+1)
		else:
			if indent:
				for tab_stop in range(level):
					print('\t',end='')
			print(item)