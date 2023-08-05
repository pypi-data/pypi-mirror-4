
""" This is a module named printoff: used to print the list element"""
def printoff(myarray):
	""" prints the element """
	for each_item in myarray:
		if isinstance(each_item, list):
			printoff(each_item)
		else:
			print(each_item)
			
' This is a module named printoff: used to print the list element'
