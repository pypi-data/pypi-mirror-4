def function_1(the_list, level=0):
    """This is my first function of python"""
    for a in the_list:
        if isinstance(a,list):
            for b in a:
                function_1(b, level+1)
        else:
            for c in  range(level):
                print("\t", end = ' ')
            print(a)
    
