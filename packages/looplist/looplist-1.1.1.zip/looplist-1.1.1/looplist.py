"""This first part tells, when you use print_looplist(list), it keeps checking
for nested lists and printing them out."""
def print_looplist(the_list):
        for items in the_list:
                if isinstance(items, list):
                        print_looplist(items)
                else:
                        print(items)