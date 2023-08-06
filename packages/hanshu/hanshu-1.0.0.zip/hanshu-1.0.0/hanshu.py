movies= ['The Holy Grail', 1975, 'Terry Jones & Terry Gilliam', 91, ['Graham Chapman', ['Michael Palin', 'John Cleese', 'Terry Gilliam', 'Eric Idle', 'Terry Jones']]]

def print_lof(the_list):
	for each_list in the_list:
		if isinstance(each_list,list):
			print_lof(each_list)
		else:
			print(each_list)

    
print_lof(movies)