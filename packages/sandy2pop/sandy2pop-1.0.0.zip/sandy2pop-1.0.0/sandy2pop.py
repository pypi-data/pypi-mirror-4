""" This is the method  it display list that it may or may not
include nested list"""
def print_list(the_list):
    """ parameter : the_list
        description : display the_list items (nested list is ok)
                    every item in its own line"""
    for list_item in the_list:
        if isinstance(list_item, list):
            print_list(list_item)
        else:
            print(list_item)
