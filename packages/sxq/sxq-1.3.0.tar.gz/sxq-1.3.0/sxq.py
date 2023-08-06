""" This is sxq.py model,and it support a function called print_lol.
    This function can deel with list"""

def print_lol(the_list,indent=False,level=0):
    """ Input a list. Recursively output a lsit in screen """
    for each_item in the_list:
        if(isinstance(each_item,list)):
                print_lol(each_item,indent,level+1)
        else:
                if indent:
                    for tab_stop in range(level):
                        print ("\t", end ="")
                    print (each_item)

