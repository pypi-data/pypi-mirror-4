"""
A simple function for recursivly printing multi deminsional lists
"""

def recursive_print( the_list ):
	for each_item in the_list:
		if isinstance( each_item, list ):
			recursive_print( each_item )
		else:
			print(each_item)
