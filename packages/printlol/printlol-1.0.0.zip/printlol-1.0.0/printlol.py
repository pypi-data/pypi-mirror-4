# -*- coding:UTF-8 -*-
movies = ["电影名称", "拍摄之时间", "导演", "时间",
          ["主角1", ["配角1", "配角2", "配角3"]]]

def print_lol(the_list):
    for item in the_list:
        if isinstance(item, list):
            print_lol(item)
        else:
            print(item)