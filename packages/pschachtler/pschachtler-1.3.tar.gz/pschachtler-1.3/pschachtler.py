# This module offers a method to print out lists that can contain other lists
# and so on. There is also a test list for testing purpose, named "testlist".

testlist = [
	"Die Ritter der Kokosnuss", 1975, "Terry Jones & Terry Gilliham", 91,
		["Graham Chapman",
			["Michael Palin", "John Cleese", "Terry Gilliham",
				"Eric Idle", "Terry Jones"]]]

def print_lvl(liste, einzug=false, ebene=0):
	# This method will print recursive every element in a list of a list...
	# in a single line.
	for element in liste:
		if isinstance(element, list):
			print_lvl(element, einzug, ebene + 1)
		else:
			if einzug == true:
				print(ebene * "\t", end='')
			print(element)

print_lvl(testlist, 0)


