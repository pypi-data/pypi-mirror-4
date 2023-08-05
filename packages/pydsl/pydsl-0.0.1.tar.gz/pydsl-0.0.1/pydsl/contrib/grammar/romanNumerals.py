#!/usr/bin/python
# -*- coding: utf-8 -*-

#Copyright (C) 2008-2012 Nestor Arocha

def matchFun(inputword):
    romanvalues = {"I":1, "V":5, "X":10, "L":50, "C":100, "D":500, "M":1000}
    nonsubstractvalues = ["V", "L", "D"]
    tmpvalues = []
    result = 0 #To check grammar we don't need the integer value, but it doesn't harm
    lastmajorvalue = None
    lastsubstractvalue = None
    lastsubstractedvalue = None
    for char in str(inputword):
        if char not in romanvalues:
            return False
        currentvalue = romanvalues[char]
        if lastmajorvalue != None and currentvalue > lastmajorvalue:
            return False
        if lastsubstractvalue != None and currentvalue >= lastsubstractvalue:
            return False
        if lastsubstractedvalue != None and currentvalue == lastsubstractedvalue:
            return False
        if len(tmpvalues) > 3:
            return False  #More than 3 symbols stored
        elif len(tmpvalues) > 0 and len(tmpvalues) < 3 and romanvalues[tmpvalues[-1]] == currentvalue:
            tmpvalues.append(char)
        elif len(tmpvalues) > 0 and romanvalues[tmpvalues[-1]] != currentvalue: #Last tmp symbol is not the same than current
            if len(tmpvalues) == 1 and romanvalues[tmpvalues[0]] < currentvalue:
                if tmpvalues[0] in nonsubstractvalues:
                    return False
                result += currentvalue - romanvalues[tmpvalues[0]] #substract the tmp value to last value
                lastsubstractvalue = currentvalue
                lastmajorvalue = currentvalue
                lastsubstractedvalue = romanvalues[tmpvalues[0]]
                tmpvalues = []
            else:  #Every tmp symbol must be the same
                firstchar = tmpvalues[0]
                for x in tmpvalues:
                    if x != firstchar:
                        return False
                if len(tmpvalues) > 1 and firstchar in nonsubstractvalues:
                    return False
                for x in tmpvalues:
                    result += romanvalues[x]
                lastmajorvalue = romanvalues[firstchar]
                tmpvalues = [char]
        elif len(tmpvalues) == 0:
            tmpvalues.append(char)
        else:
            return False
    for x in tmpvalues:
        if (lastmajorvalue != None and romanvalues[x] > lastmajorvalue) or (lastsubstractedvalue!= None and romanvalues[x] >= lastsubstractvalue):
            return False
        #TODO: Check for contiguous nonsubstractvalues
        result += romanvalues[x]
    return True

iclass = "PythonGrammar"
