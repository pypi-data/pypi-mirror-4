"""This first part tells, when you use print_looplist(list), it keeps checking
for nested lists and printing them out."""
def print_looplist(the_list, indent=false, level=0):
        for items in the_list:
                if isinstance(items, list):
                        print_looplist(items, indent, level+1)
                else:
                        if indent:
                            for tab_stop in range(level):
                                    print('\t', end='')
                        print(items)