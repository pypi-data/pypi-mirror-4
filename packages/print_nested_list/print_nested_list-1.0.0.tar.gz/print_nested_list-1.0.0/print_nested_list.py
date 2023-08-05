"""This module was created in order to allow the printing
of a list with an arbitrary number of nested lists"""

""" Takes a list as it's input
If any item in the list is a list itself, the function
recurses and proceeds"""

def print_lol(a_list):
	for each_item in a_list:
		if isinstance(each_item, list):
			print_lol(each_item)
		else:
			print(each_item)	
