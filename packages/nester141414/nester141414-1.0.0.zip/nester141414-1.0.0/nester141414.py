"""Standard way to iterate through and print items within a list. Free for all to use.""" 
def printlul(tl):
	"""Iterate through tl(the list) and find ei(each item). If there is a list within ei, continue iterating,
	else print contents of the list."""
	for ei in tl:
		if isinstance(ei, list):
			printlul(ei)
		else:
			print ei

			

