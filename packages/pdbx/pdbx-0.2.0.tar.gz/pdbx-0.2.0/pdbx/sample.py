#!/usr/bin/python
# coding:utf-8 

'''
Created on 2013-3-22

@author: stone
'''

from pdbx import Rpdb
import random
import time

def add(i, j):
    '''func for add'''
    r = i + j
    return r

def main():
    rpdb = Rpdb()                # Debugger started. Port is 8787(Default Value),   Suspend is True(Default Value)
    # rpdb = Rpdb(9898)          # Debugger started. Port is 9898(Specified Value), Suspend is True(Default Value)
    # rpdb = Rpdb(suspend=False) # Debugger started. Port is 8787(Default Value),   Suspend is False(Specified Value) 
    # rpdb = Rpdb(9898, False)   # Debugger started. Port is 9898(Specified Value), Suspend is False(Specified Value) 
    while True:
        rpdb.set_trace()
        i = random.randint(1, 10)
        j = random.randint(1, 10)
        r = add(i, j)
        print r
        time.sleep(1)

if __name__ == '__main__':
    main()
