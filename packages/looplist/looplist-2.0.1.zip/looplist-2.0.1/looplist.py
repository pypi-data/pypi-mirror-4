import sys
def looplist(the_list, indent=False, level=0, fh=sys.stdout):
    for items in the_list:
        if isinstance(items, list):
            looplist(items, indent, level+1, fh)
        else:
            if indent:
                for tab_stop in range(level):
                    print('\t', end='', file=fh)
            print(items, file=fh)
