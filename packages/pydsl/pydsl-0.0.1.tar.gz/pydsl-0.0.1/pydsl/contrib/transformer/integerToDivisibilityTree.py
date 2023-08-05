#!/usr/bin/python
# -*- coding: utf-8 -*-

def function(inputdic, auxboarddic, inputgt, outputgt):
    output = ""
    if not inputdic["input"]: 
        return {}
    numberlist = [inputdic["input"]]
    while len(numberlist) > 0:
        childnumber = auxboarddic["divisor"]({"input":numberlist[0]})
        if not "output" in childnumber:
            break
        relationlist = str(childnumber["output"]).split(";")
        for relation in relationlist:
            if relation:
                relationcomp = relation.split("\0parent\0")
                output += relation + ";"
                numberlist.append(relationcomp[1])
        del numberlist[0]
    return {"output":output}

iclass = "HostPythonTransformer"
inputdic = {"input":"integer"}
outputdic = {"output":"IntegerTree"}
auxdic = {"divisor":"integerDivisor"}
