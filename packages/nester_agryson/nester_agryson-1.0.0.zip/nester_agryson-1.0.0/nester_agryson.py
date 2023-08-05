"""
This module "nester.py" provides a function called "printList()" which accepts a list as an argument and prints the contents, whether nested or not.
"""
def printList(list_in):
	"""
	"printList()" will recursiveley print all items in a list "list_in" and its nested lists
	"""
	for item in list_in:
		if isinstance(item, list):
			printList(item)
		else:
			print(item)