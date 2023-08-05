#!/usr/bin/python
# -*- coding: utf-8 -*-

def function(inputdic, inputg, outputg):
    stt = inputg["input"].get_trees(inputdic["input"])
    for tree in stt:
        treelist = tree.getAllByOrder()
        treelist.reverse()
        stack = []
        for element in treelist: 
            #Coleccionar los elementos con el mismo padre
            #Obtener la regla aplicada
            #Llamar a la funcion reductoria con la regla mas todos los DescentParserResult
            if len(element.symbollist) == 1:
                from pydsl.Grammar.Symbol import NonTerminalSymbol
                if isinstance(element.symbollist[0], NonTerminalSymbol):
                    if element.symbollist[0].name == "Expression":
                        stack.append("RE")


        #print treelist[0].symbollist
        #print [ele.symbollist for ele in treelist[0].childlist]
        
    return {"output":"True"}

inputdic = {"input":"LogicalExpression"}
outputdic = {"output":"TrueFalse"}
iclass = "PythonTransformer"
