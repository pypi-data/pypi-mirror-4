"""
A simple function for recursivly printing multi deminsional lists
"""

def recursive_print( the_list, tabular = False, stack_level = 0 ):
	for each_item in the_list:
		if isinstance( each_item, list ):
			recursive_print( each_item, tabular, stack_level + 1 )
		else:
			string = ""
			if tabular:
				for i in range( stack_level ):
					string += "\t"
			string += str(each_item)
			print(string)
