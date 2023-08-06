'''这是一个列表模块'''
def dylist(bname,level=0):
    '''主要内容为一个循环套'''
    for abc in bname:
        if isinstance(abc,list):
                      dylist(abc,level+1)
        else:
            for tab_stop in range(level):
                print('\t',end='')
            print(abc)
                      
