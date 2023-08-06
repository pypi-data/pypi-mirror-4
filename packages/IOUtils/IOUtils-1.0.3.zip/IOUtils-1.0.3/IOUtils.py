"""Print all elements in List.
   Param1: List name<String>
   Param2: Indent or not<Boolean, default value=True>
   Param3: Indent start position<int, default value=0>"""
def printList(items,indent=True,level=0):
    if(indent!=True):
        level=-1
    for item in items:
        if(isinstance(item,list)):
            if(level<0):
                printList(item,False,level)
            else:
                printList(item,True,level+1)
        else:
            if(level<=0):
                print(item)
            else:
                for num in range(level):
                    print('\t',end='')
                print(item)
