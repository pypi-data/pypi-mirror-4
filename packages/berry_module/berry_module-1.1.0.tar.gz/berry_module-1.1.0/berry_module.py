"""This is a simple module to print the data items within a nested list"""
def print_lol(items,level):
    for each_item in items:
        if isinstance(each_item, list):
            print_lol(each_item,level+1)
        else:
            for tab_stop in range(level):
                print("\t",end='')
            print(each_item)


        
