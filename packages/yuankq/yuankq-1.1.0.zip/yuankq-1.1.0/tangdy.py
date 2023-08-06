"""这是一个列表打印模块，函数名为DY"""
def dy(bm,sj):
    """这是函数DY的代码段，bm为列表名,sj为缩进控制"""
    for t in bm:
        if isinstance(t,list):
            dy(t,sj+1)
        else:
            for m in range(sj):
                print('\t',end='')
            print(t)
        
