def looplist(the_list, indent=False, level=0):
        for items in the_list:
                if isinstance(items, list):
                        looplist(items, indent, level+1)
                else:
                        if indent:
                            for tab_stop in range(level):
                                print("\t", end='')
                        print(items)