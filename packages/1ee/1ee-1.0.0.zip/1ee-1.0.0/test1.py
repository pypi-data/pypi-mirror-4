#这是"test.py"模块,提供了一个名为print_lol函数，该函数的作用是打印列表,其中也可能包含列表
#或者嵌套列表
def print_lol(the_list):
    #这个函数取一个位置参数，名为the_list，这可以是任何test.py的列表
    for each_item in the_list:
        if isinstance(each_item,list):
            print_lol(each_item)
        else:
            print(each_item)
