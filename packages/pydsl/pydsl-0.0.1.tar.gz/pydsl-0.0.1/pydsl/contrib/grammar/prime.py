#!/usr/bin/python
# -*- coding: utf-8 -*-

#Copyright (c) 2008-2012 Nestor Arocha Rodriguez

"""Prime number"""

def matchFun(input):
    number = str(input)
    try:
        number = int(number)
    except ValueError:
        return False
    if number < 0: return False
    if number < 3: return True
    n = 2
    while n <= number/2:
        if number % n == 0:
            return False
        n += 1
    return True


iclass = "PythonGrammar"

