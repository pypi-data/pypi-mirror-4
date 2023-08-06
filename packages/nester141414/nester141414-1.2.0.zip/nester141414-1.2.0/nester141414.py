"""Standard way to iterate through and print items within a list. Free for all to use.""" 
def printlul(tl,level=0):
	"""Iterate through tl(the list) and find ei(each item). If there is a list within ei, continue iterating,
	else print contents of the list."""
	for ei in tl:
		if isinstance(ei, list):
			printlul(ei,level+1)
		else:
			for n in range(level):
				print ("\t",end='')
			print (ei)
			

