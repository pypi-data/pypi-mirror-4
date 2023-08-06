"""This is the olnesty module, and it provides one function which simply demonstrates
recursion.  It works with nested lists."""


def print_lol(the_list):
    """this is an example function which demonstrates recursion"""
    for each_item in the_list:
        if isinstance(each_item, list):
            print_lol(each_item)
        else:
            print(each_item)
            
