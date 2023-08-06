"""这是一个列表打印模块，函数名为DY"""
def dy(bm):
    """这是函数DY的代码段，bm为列表名"""
    for t in bm:
        if isinstance(t,list):
            dy(t)
        else:
            print(t)
        
