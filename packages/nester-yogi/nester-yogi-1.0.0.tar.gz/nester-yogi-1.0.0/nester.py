"""this is a nester module!"""
def innerlist(inlist,level):
    """this is the nester function!"""
    for eachitem in inlist:
        if isinstance(eachitem, list):
            innerlist(eachitem,level+1)
        else:
            for tab_stop in range(level):
                print('\t',end='')
            print(eachitem)