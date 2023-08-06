def lol_print(my_list):
    for elem in  my_list:
        if(isinstance(elem,list)):
            lol_print(elem)
        else:
            print(elem)
