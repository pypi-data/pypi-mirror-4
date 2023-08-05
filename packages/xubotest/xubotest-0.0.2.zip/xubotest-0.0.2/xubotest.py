def print_lol(aList,level=0):
    for e1 in aList:
        if isinstance(e1,list):
            print_lol(e1,level+1)
        else:
            for tab in range(level):
                print("\t"),
            print e1
