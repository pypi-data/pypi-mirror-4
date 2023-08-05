def print_lol(aList):
    for e1 in aList:
        if isinstance(e1,list):
            print_lol(e1)
        else:
            print e1
