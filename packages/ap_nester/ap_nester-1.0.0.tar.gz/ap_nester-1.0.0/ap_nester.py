"""This is a function used to diplay all the nested lists listed in a list"""
def disp_lists(the_list):
    """takes the argument the_list for the user defined list and then used to
    recursively call the list"""
    for outside in the_list:
        if isinstance(outside, list):
            disp_lists(outside)
        else:
            print(outside)
            
