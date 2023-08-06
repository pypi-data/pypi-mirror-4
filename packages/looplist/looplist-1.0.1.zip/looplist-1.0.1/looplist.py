"""This first part tells, when you use print_looplist(list), it keeps checking
for nested lists and printing them out."""
def print_looplist(the_list):
        for items in the_list:
                if isinstance(items, list):
                        print_looplist(items)
                else:
                        print(items)
"""This second part gives a double-nested module. Try using print_looplist(movies)
   on it!"""                
movies = [
    "The Holy Grail", 1975, 'Terry Jones & Terry Gilliam', 91, 
            ["Graham Chapman",
                    ["Michael Palin", 'John Cleese', 'Terry Gilliam', 'Eric Idle', 'Terry Jones']]]
