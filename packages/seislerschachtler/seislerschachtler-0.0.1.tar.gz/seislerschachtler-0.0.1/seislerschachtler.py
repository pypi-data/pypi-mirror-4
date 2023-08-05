def print_lvl(liste, einrücken=False, level = 0):
	""" Beispiel um Listen auszudrucken 
        Gemäss "Python von Kopf bis Fuss" - Kapitel 2 
    """
	for element in liste:
		if isinstance(element, list):
			print_lvl(element, einrücken, level+1)
		else:
			if einrücken:
				print("\t" * level, end='')
			print(element)