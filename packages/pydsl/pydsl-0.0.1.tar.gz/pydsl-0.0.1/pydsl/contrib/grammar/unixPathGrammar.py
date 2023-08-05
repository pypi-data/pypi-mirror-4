#!/usr/bin/python
# -*- coding: utf-8 -*-

#Copyright (C) 2008-2011 Néstor Arocha Rodríguez

"""unixPaths language"""

#unixPaths follow the expression /[<name>{/<name>}]

def matchFun(inputd):
    import os 
    if os.path.exists(str(inputd)):
        return True
    return False

iclass = "PythonGrammar"
