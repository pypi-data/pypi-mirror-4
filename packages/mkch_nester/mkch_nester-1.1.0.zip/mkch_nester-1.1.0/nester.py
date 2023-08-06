def lol_print(my_list,index):
    for item in my_list:
        if(isinstance(item,list)):
            lol_print(item,index+1)
        else:
            for i in range(index):
                print('\t',end='')
            print(item)
