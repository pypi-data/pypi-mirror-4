#!/usr/bin/python
# -*- coding: utf-8 -*-

#Copyright (C) 2008-2012 Néstor Arocha Rodríguez

"""IntegerTreeGrammar language"""

#{<int>\0parent\0<int>;}

def matchFun(input, aux):
    parentrelationlist = str(input).split(";")
    for parentrelation in parentrelationlist:
        relation = parentrelation.split("\0")
        if len(relation) < 2:
            break
        if len(relation) != 3:
            return False
        if relation[1] != "parent":
            return False
        if not aux["int"].check(relation[0]):
            return False
        if not aux["int"].check(relation[2]):
            return False
    return True


iclass = "PythonGrammar"
auxdic =  {"int":"integer"}
