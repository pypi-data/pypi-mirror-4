"""This module was created in order to allow the printing
of a list with an arbitrary number of nested lists"""

""" Takes a list and a number as it's input
If any item in the list is a list itself, the function
recurses and proceeds.  For any non-list encountered,
the function indents by a number of tab stops equal
to the number given."""
def print_lol(a_list, level):
	for each_item in a_list:
		if isinstance(each_item, list):
			print_lol(each_item, level+1)
		else:
			for tab_stop in range(level):
				print("\t")
			print(each_item)	
