'''这是test模块'''
def print_list(li):
    '''这是print_list函数'''
    for key in li:
        if isinstance(key,list):
            print_list(key)
        else:
            print(key)
