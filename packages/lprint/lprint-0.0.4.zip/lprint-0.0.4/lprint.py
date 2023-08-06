"""this module includes the function capable of displaying each item in the list and its nested lists"""
import sys
def print_lol(the_list, indent=False,level=0,fh=sys.stdout):
    for item in the_list:
        if isinstance(item, list):
            print_lol(item,indent,level+1,fh)
        else:
                        if indent:
                                print("\t"*level, end='',file=fh)
#                                for enum in range(level):
#                                        print("\t",end='')
                        print(item,file=fh)
