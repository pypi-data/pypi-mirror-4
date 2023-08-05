#!/usr/bin/python
# -*- coding: utf-8 -*-

#Copyright (C) 2008-2012 Nestor Arocha


def function(inputdic):
    output = ""
    if inputdic["input"].getContent() == "": 
        return {}
    parentpath = inputdic["input"]
    import os
    if not os.path.exists(parentpath) or not os.path.isdir(parentpath):
        return {"output":""}
    if not os.access(parentpath, os.R_OK & os.X_OK):
        return {"output":""}
    filelist = os.listdir(parentpath)

    for filename in filelist:
        output += parentpath + "/" + filename + ";"
    return {"output":output}

iclass = "PythonTransformer"
inputdic = {"input":"unixPathGrammar"}
outputdic = {"output":"unixPathListGrammar"}
