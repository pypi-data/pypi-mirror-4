"""这是一个列表打印模块，函数名为DY"""
def dy(bm,bz=False,sj=0):
    """这是函数DY的代码段，bm为列表名,bz为是否缩进标志，sj为缩进控制TAB数"""
    for t in bm:
        if isinstance(t,list):
            dy(t,bz,sj+1)
        else:
            if bz:
                for m in range(sj):
                    print('\t',end='')
            print(t)
        
