movies= ['The Holy Grail', 1975, 'Terry Jones & Terry Gilliam', 91,
['Graham Chapman', ['Michael Palin', 'John Cleese', 'Terry Gilliam',
'Eric Idle', 'Terry Jones']]]

def print_lof(the_list,level):
        for each_list in the_list:
                if isinstance(each_list,list):
                        print_lof(each_list,level+1)
                else:
                        for tab_stop in range(level):
                                print("\t",end='')
                        print(each_list)

print_lof(movies,0)
