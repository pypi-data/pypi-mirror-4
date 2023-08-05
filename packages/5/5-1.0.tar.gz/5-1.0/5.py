#aaa=['1','2','3',['4']]
def   pop(the_list):
        for a in  the_list:
                if isinstance(a,list):
                        pop(a)
                else:
                        print (a)
#pop(aaa)
