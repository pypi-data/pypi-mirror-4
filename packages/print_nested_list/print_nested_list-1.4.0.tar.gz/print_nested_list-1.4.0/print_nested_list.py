"""This module was created in order to allow the printing
of a list with an arbitrary number of nested lists"""

""" 

Takes a list, a boolean, a number, and an output method as it's input
If any item in the list is a list itself, the function
recurses and proceeds.  For any non-list encountered,
the function indents by a number of tab stops equal
to the number given.  The default indenting behavior is 
FALSE, with no indents, and can be enabled by passing
TRUE into the function.

"""
def print_lol(a_list, indent=False, level=0, output=sys.stdout):
	for each_item in a_list:
		if isinstance(each_item, list):
			print_lol(each_item, indent, level+1, output)
		else:
			if indent:
				for tab_stop in range(level):
					print("\t", end="", file=output)
			print(each_item, file=output)	
