#!/usr/bin/python
# -*- coding: utf-8 -*-

#This file is part of ColonyDSL.

"""Universal Store Input Grammar"""

from pydsl.Grammar.Symbol import StringTerminalSymbol as _CTS , WordTerminalSymbol as _WTS, NonTerminalSymbol as _NTS, BoundariesRules as _BR
from pydsl.Grammar.BNF import Production as _NTP 

_br = _BR("max", 1) 

_symbol1 = _CTS("S")
_symbol2 = _CTS("R")
_symbol3 = _CTS(":")
_symbol4 = _WTS("Integer", {"grammarname":"integer"}, _br)
_symbol5 = _WTS("Generic", {"grammarname":"cstring"}, _br)

_final1 = _NTS("storeexp") 
_final2 = _NTS("retrieveexp") 
initialsymbol = _NTS("exp")

_rule1 = _NTP([_final1], [_symbol1, _symbol3, _symbol5])
_rule2 = _NTP([_final2], [_symbol2, _symbol3, _symbol4])
_rule3 = _NTP([initialsymbol], [_final1])
_rule4 = _NTP([initialsymbol], [_final2])
fulllist = [_rule1, _rule2, _rule3, _rule4, _symbol1, _symbol2, _symbol3, _symbol4, _symbol5]


iclass = "SymbolGrammar"
#parser = "descent"
