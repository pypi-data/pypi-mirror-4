"""this is my first .py
kcrosswind
bupt"""

def print_lol(the_list):
    for meta in the_list:
        if isinstance(meta,list):
            print_lol(meta)
        else:
            print(meta)
