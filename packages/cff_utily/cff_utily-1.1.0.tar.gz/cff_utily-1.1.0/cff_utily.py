#-*- coding: UTF-8 -*-
"""这是‘nester.py’模块，提供了一个print_lol函数，这个函数的作用是打印列表，其中有可能包含(也可能不包含)嵌套列表"""
def print_lol(the_list,level):
    """这个函数取一个位置参数，名为the_list，这可以是任何Python列表(也可以是包含嵌套列表的列表)。所指定的列表中的每个数据项会(递归)输出到屏幕上，各数据项各占一行。
       第二个参数(名为level)用来在遇到嵌套列表的时候插入制表符
    """
    for each in the_list:
        if isinstance(each,list):
            print_lol(each,level+1)
        else:
            for tab_stop in range(level):
                print('\t'),
            print(each)
