# -*- coding:UTF-8 -*-
movies = ["电影名称", "拍摄之时间", "导演", "时间",
          ["主角1", ["配角1", "配角2", "配角3"]]]

"""这是"printlol"模块，提供了一个叫做print_lol()的函数
"""

def print_lol(the_list, level):
    for item in the_list:
        if isinstance(item, list):
            print_lol(item, level+1)
        else:
            for tab_stop in range(level):
                print("\t", end="")
            print(item)

#print_lol(movies, 0)
