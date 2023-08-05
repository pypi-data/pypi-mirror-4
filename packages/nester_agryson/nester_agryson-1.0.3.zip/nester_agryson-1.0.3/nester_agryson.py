"""
This module "nester.py" provides a function called "printList()" which accepts a list as an argument and prints the contents, whether nested or not. with appropriate indentation
"""
def printList(list_in, indent=False, level=0):
	"""
	"printList()" will recursiveley print all items in a list "list_in" and its nested lists, indenting children by the vaue provided by "indent"
	"""
	for item in list_in:
		if isinstance(item, list):
			printList(item, indent, level+1)
		else:
			if indent:
				for tabs in range(level):
					print("\t", end="")
			print(item)