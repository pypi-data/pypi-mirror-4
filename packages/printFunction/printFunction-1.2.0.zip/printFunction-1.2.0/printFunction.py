''' fsdafasefsd
fawefds
feawfasdf
afefefffffffffffffffff
'''
def printList(_list,level=0):
        """        1156456        """
        for var in _list:
                if isinstance(var,list):
                        printList(var,level+1)
                else:
                        for tabStep in range(level):
                                print("\t",end='')
                        print(var)
