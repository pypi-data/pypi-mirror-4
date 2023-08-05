#!/usr/bin/python
# -*- coding: utf-8 -*-

#Copyright (C) 2008-2011 Nestor Arocha

def function(inputdic, auxdic, inputgt, outputgt):
    content = inputdic["input"]
    outputfilename = inputdic["outfile"]
    import subprocess
    process = subprocess.Popen(["dot","-Tpng","-o",outputfilename],stdin = subprocess.PIPE)
    presult = process.communicate(input = content.encode())
    result = auxdic["read"].call({"input":outputfilename})
    return {"output":"True"}

iclass = "HostPythonTransformer"
inputdic = {"input":"dotLanguageGrammar","outfile":"cstring"}
outputdic = {"output":"TrueFalse"}
auxdic = {"read":"read"}

