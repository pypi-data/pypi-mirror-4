""" A Begineers Module """
def print_List_In_Recursive_Fashion(toprintList, level):
	""" A method that recirsively prints a list
	    inside a list """
	for each_Item in toprintList:
		if(isinstance(each_Item,list)):
			print_List_In_Recursive_Fashion(each_Item, level+1)
		else:
			for each in range(level):
				print("*")
			print(each_Item)
