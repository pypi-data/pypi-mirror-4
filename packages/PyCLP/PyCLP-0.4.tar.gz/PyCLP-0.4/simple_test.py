'''
Created on Nov 23, 2012

@author: radice
'''
from pyclp import *
def my_print(arguments):
    print (type(arguments[0]))
    res=unify(Atom(1),arguments[1])
    print(res)
    print("caio")
    print (arguments)
    return None
    
if __name__ == '__main__':
    init()
    register_function(Atom('eclipse'))
    add_python_predicate("extpred",my_print)
    my_var=Var()
    Compound('call_python',"extpred",[1,my_var,3,Compound("Ciccia",1,2,[1,"cas"])]).post_goal()
    res, pipe=resume()
    print(res,pipe)
    if res == FLUSHIO:
        my_stream=Stream(pipe)
        print(my_stream.readall())
    print(resume())
    print (my_var.value())
    cleanup()
   