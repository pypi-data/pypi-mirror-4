"""
This module "nester.py" provides a function called "printList()" which accepts a list as an argument and prints the contents, whether nested or not. with appropriate indentation
"""
def printList(list_in, indent=0):
	"""
	"printList()" will recursiveley print all items in a list "list_in" and its nested lists, indenting children by the vaue provided by "indet"
	"""
	for item in list_in:
		if isinstance(item, list):
			printList(item, indent+1)
		else:
			for tabs in range(indent):
				print("\t", end="")
			print(item)