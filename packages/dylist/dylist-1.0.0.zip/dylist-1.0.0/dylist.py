'''这是一个列表模块'''
def dylist(bname):
    '''主要内容为一个循环套'''
    for abc in bname:
        if isinstance(abc,list):
                      dylist(abc)
        else:
                      print(abc)
                      
