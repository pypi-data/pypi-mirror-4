""" This is sxq.py model,and it support a function called print_lol.
    This function can deel with list"""

def print_lol(the_list):
    """ Input a list. Recursively output a lsit in screen """
    for each_item in the_list:
        if(isinstance(each_item,list)):
                print_lol(each_item)
        else:
                print each_item
