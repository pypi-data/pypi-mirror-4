#!/usr/bin/python
# -*- coding: utf-8 -*-

#Copyright (C) 2008-2012 Nestor Arocha


def function(inputdic, auxboarddic):
    output = ""
    if inputdic["input"].getContent() == "": 
        return {}
    pendantpaths = [inputdic["input"]]
    while pendantpaths > 0:
        childlistdic = auxboarddic["pathChild"].processWords({"input":pendantpaths[0]})
        if not childlistdic.has_key("output"):
            break
        childlist = childlistdic["output"].split(";")
        for path in childlist:
            if path:
                output += pendantpaths[0] + "\0" + "parent" +"\0" + path + ";"
                pendantpaths.append(path)
        del pendantpaths[0]
    return {"output":output}

iclass = "HostPythonTransformer"
inputdic = {"input":"unixPathGrammar"}
outputdic = {"output":"unixPathTreeGrammar"}
auxdic = {"pathChild":"unixPathChildGenerator"}
