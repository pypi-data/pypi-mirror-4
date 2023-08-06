"""循环输出List中所有元素，包括嵌套的List
   level=0则不输入缩进，level>=1开始根据嵌套的深度输出缩进"""
def printList(items,level=0):
    for item in items:
        if(isinstance(item,list)):
            if(level==0):
                printList(item,level)
            else:
                printList(item,level+1)
        else:
            if(level==0 or level==1):
                print(item)
            else:
                for num in range(level-1):
                    print('\t',end='')
                print(item)
