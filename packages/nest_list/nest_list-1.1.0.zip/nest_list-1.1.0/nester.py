'''
    Prints all items in a list including any nested list item
'''

def print_list(lst, indent=False,level=0):

    for list_item in lst:

        if isinstance(list_item, list):
           print_list(list_item, indent, level+1)

        else:
            if indent:
                for tabspace in range(level):
                    print("\t", end='')
            print(list_item)

           
