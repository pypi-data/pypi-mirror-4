"""Module "creeky_schachtler.py". Provides a function print_lvl() which prints a list no matter how many lists in the list are included. And yes: this is really just a simple sample from that python book."""

def print_lvl(liste, einzug=False,ebene=0):
	"""The mandatory argument list should consist of a list. No matter how many lists in the list are included. Each element of list will be recursively printed on the standard output."""
	for element in liste:
		if isinstance(element, list):
			print_lvl(element, einzug, ebene+1)
		else:
			if einzug:
				for tab_stop in range(ebene):
					print("\t", end=' ')
			print(element)

