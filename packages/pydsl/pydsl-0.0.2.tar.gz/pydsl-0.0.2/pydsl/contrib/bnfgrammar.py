"""BNF grammars for testing"""

from pydsl.Grammar.Symbol import StringTerminalSymbol, WordTerminalSymbol, NonTerminalSymbol, NullSymbol
from pydsl.Grammar.BNF import Production, BNFGrammar
from pydsl.Memory.File.BNF import strlist_to_production_set

br = "max"
leftrecursive=["S ::= E","E ::= E dot | dot","dot := String,."]
rightrecursive=["S ::= E","E ::= dot E | dot","dot := String,."]
centerrecursive=["S ::= E","E ::= dot E dot | dot","dot := String,."]


#productionset1 definition
symbol1 = StringTerminalSymbol("S")
symbol2 = StringTerminalSymbol("R")
symbol3 = StringTerminalSymbol(":")
symbol4 = WordTerminalSymbol("Integer", {"grammarname":"integer"}, br)
symbol5 = WordTerminalSymbol("Generic", {"grammarname":"cstring"}, br)
final1 = NonTerminalSymbol("storeexp") 
final2 = NonTerminalSymbol("retrieveexp") 
final3 = NonTerminalSymbol("exp")
rule1 = Production([final1], [symbol1, symbol3, symbol5])
rule2 = Production([final2], [symbol2, symbol3, symbol4])
rule3 = Production([final3], [final1])
rule4 = Production([final3], [final2])
rulelist = [rule1, rule2, rule3, rule4, symbol1, symbol2, symbol3, symbol4, symbol5]
productionset1 = BNFGrammar(final3, rulelist)

#productionset2 definition
symbola = StringTerminalSymbol("A")
symbolb = StringTerminalSymbol("B")
nonterminal = NonTerminalSymbol("res")
rulea = Production ([nonterminal], [symbola, NullSymbol(), symbolb])
productionset2 = BNFGrammar(nonterminal, [rulea, symbola, symbolb])
productionsetlr = strlist_to_production_set(leftrecursive)
productionsetrr = strlist_to_production_set(rightrecursive)
productionsetcr = strlist_to_production_set(centerrecursive)


#tokenlist definition
string1 = "S:a"
string2 = "S:"
string3 = "AB"
string4 = "ACB"
dots = "....."
