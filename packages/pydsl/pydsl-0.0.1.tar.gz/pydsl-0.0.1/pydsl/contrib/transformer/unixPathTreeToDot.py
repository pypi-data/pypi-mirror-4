#!/usr/bin/python
# -*- coding: utf-8 -*-

def function(inputdic):
    output = "digraph graphname \n{ "
    if inputdic["input"].getContent() == "": 
        return {}
    parentshiplist = inputdic["input"].getContent().split(";")
    for parentship in parentshiplist:
        dirpair = parentship.split("\0parent\0")
        if len(dirpair) !=2:
            break
        output += '"' + dirpair[0] + '" -> "' + dirpair[1] + "\"\n"
    output += "}"
    return {"output":output}

iclass = "PythonTransformer"
inputdic = {"input":"unixPathTreeGrammar"}
outputdic = {"output":"dotLanguageGrammar"}

