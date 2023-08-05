#!/usr/bin/python
# -*- coding: utf-8 -*-

#Copyright (C) 2008-2012 Nestor Arocha 

"""unixFileTree language"""

#{<path>\0parent\0<path>;}

def matchFun(inputw, auxdic):
    parentrelationlist = str(inputw).split(";")
    for parentrelation in parentrelationlist:
        relation = parentrelation.split("\0")
        if len(relation) < 2:
            break
        if len(relation) != 3:
            return False
        if relation[1] != "parent":
            return False
        if not auxdic["unixpath"].check(relation[0]):
            return False
        if not auxdic["unixpath"].check(relation[2]):
            return False
    return True


iclass = "PythonGrammar"
auxdic = {"unixpath":"unixPathGrammar"}
