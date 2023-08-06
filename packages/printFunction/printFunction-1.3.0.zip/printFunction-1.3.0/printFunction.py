''' fsdafasefsd
fawefds
feawfasdf
afefefffffffffffffffff
'''
def printList(_list,isIndent=False,level=0):
        """        1156456        """
        for var in _list:
                if isinstance(var,list):
                        printList(var,level+1)
                else:
                        if isIndent:
                                for tabStep in range(level):
                                        print("\t",end='')
                        print(var)
