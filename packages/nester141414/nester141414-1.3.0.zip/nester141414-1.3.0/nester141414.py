"""Standard way to iterate through and print items within a list. Free for all to use.""" 
def printlul(tl, indent=False, level=0):
	"""Iterate through tl(the list) and find ei(each item). If there is a list within ei, continue iterating,
	else print contents of the list."""
	for ei in tl:
		if isinstance(ei, list):
			printlul(ei,indent,level+1)
		else:
			if indent == True:
				for n in range(level):
					print ("\t",end='')
			print (ei)
			

