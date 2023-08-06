""" This a func. taht splits inner lists of any level
        It also displays each element in order"""



def print_list(x):
    """ This func. checks for each and every elementfor
        a list and if it is a list then it recurrsively
        calls the func and applies the same procedure again
        on it, and hence does the same ting on and on again."""
    
    for each_item in x:
        if isinstance(each_item, list):
            print_list(each_item)

        else:
            print(each_item)

