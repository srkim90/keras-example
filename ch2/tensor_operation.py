# -*- coding: utf-8 -*-

'''
  Author   : Kim, Seongrae
  Filename : tensor_operation.py
  Release  : 1
  Date     : 2020-02-02
 
  Description : tensor operation test
 
  Notes :
  ===================
  History
  ===================
  2020/02/02  created by Kim, Seongrae
'''


# common package import
import os
import json
import numpy as np

def main():

    print('1. numpy 연산')
    x = np.array([1000,2,3,4,1115,6,7,8,9,10])
    y = np.array([10,20,30,40,50,60,70,80,90,100])
    print(np.maximum(y,x))  # [1000   20   30   40 1115   60   70   80   90  100] , 각각의 index 1:1 비교, 큰 값의 list를 만든다. (shape 이 동일해야 함)
    z = x + y
    print(z) # [ 11  22  33  44  55  66  77  88  99 110]

    print('2. tensor product(텐서 곱셈)')
    x = np.random.random((64 , 3, 32, 10))
    y = np.random.random(        (32, 10))
    z = np.maximum(x,y)
    print("z: shape=%s, dtype=%s, ndim=%d" % (z.shape, z.dtype, z.ndim))

    x = np.random.random((64 , 3, 32, 10))
    y = np.random.random(        (31, 10))
    try:
        z = np.maximum(x,y)
    except:
        print('This is Error')

    print('2. tensor reshaping')
    x = np.random.random((6000, 28, 28)) 
    print("x.shape : %s " % (x.shape,))
    x1 = x.reshape(6000,28*28)
    x2 = x.reshape(6000,-1)
    x3 = x.reshape(-1)
    x4 = x3.reshape(6000, 28, 28)
    print("x1.shape      : %s " % (x1.shape,))
    print("x2.shape      : %s " % (x2.shape,))
    print("x3.shape      : %s " % (x3.shape,))
    print("x4.shape      : %s " % (x4.shape,))
    print("is x4 == x  ? : %s " % (np.array_equal(x, x4)))
    print("is x4 == x1 ? : %s " % (np.array_equal(x1, x4)))

if __name__ == "__main__":
    main()
